from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from .models import Product, Sales, Arrival, SoldProduct, ArrivedProduct, Company, Role

User = get_user_model()

class ProductSerializer(serializers.ModelSerializer):
	class Meta:
		model = Product
		fields = ('id', 'name', 'description', 'amount_left', 'wholesale_price', 'retail_price', 'barcode', 'vendor_name', 'manufacturer', 'owner')
		read_only_fields = ('owner',)

class SoldProductSerializer(serializers.ModelSerializer):
	class Meta:
		model = SoldProduct
		fields = ('id', 'name', 'barcode', 'amount', 'retail_price', 'wholesale_price', 'sales')
		read_only_fields = ('retail_price', 'wholesale_price', 'name', 'description', 'sales')

class SalesSerializer(serializers.ModelSerializer):
	sold_products = SoldProductSerializer(many=True)
	class Meta:
		model = Sales
		fields = ('id', 'date', 'owner', 'sold_products')
		read_only_fields = ('owner', 'date')

	def create(self, validated_data):
		request = self.context.get('request', None)
		if request is None or request.user.is_anonymous():
			raise serializers.ValidationError("Must be logged in to make a sales.")
		products_data = validated_data.pop('sold_products')
		sales = Sales.objects.create(owner=request.user, date=timezone.now(), **validated_data)
		for product_data in products_data:
			amount = product_data['amount']
			barcode = product_data['barcode']
			product = Product.objects.get(barcode=barcode)
			print(product)
			product.amount_left -= Decimal(amount)
			product.save()
			SoldProduct.objects.create(
				sales=sales, 
				name = product.name,
				wholesale_price=product.wholesale_price, 
				retail_price=product.retail_price, 
				description=product.description, 
				**product_data
			)
		return sales

class ArrivedProductSerializer(serializers.ModelSerializer):
	class Meta:
		model = ArrivedProduct
		fields = ('id', 'name', 'description', 'barcode', 'amount', 'wholesale_price',
			'retail_price', 'vendor_name', 'manufacturer', 'arrival')

class ArrivalSerializer(serializers.ModelSerializer):
	arrived_products = ArrivedProductSerializer(many=True)
	class Meta:
		model = Arrival
		fields = ('id', 'date', 'owner', 'arrived_products')
		read_only_fields = ('owner', 'date')

	def create(self, validated_data):
		request = self.context.get('request', None)
		if request is None and request.user.is_anonymous():
			raise serializers.ValidationError("Must be logged in to make an arrival.")
		products_data = validated_data.pop('arrived_products')
		arrival = Arrival.objects.create(owner=request.user, date=timezone.now(), **validated_data)
		for product_data in products_data:
			barcode = product_data['barcode']
			product, created = Product.objects.get_or_create(barcode=barcode)
			product.amount_left += product_data['amount']
			product.wholesale_price = product_data['wholesale_price']
			product.retail_price = product_data['retail_price']
			product.name = product_data['name']
			product.description = product_data.get('description', '')
			product.vendor_name = product_data.get('vendor_name', '')
			product.manufacturer = product_data.get('manufacturer', '')
			product.save()
			ArrivedProduct.objects.create(arrival=arrival, **product_data)
		return arrival

class UserSerializer(serializers.ModelSerializer):
	password = serializers.CharField(write_only=True, required=False)
	company_name = serializers.CharField(write_only=True, required=True)	

	class Meta:
		model = User
		fields = ('id', User.USERNAME_FIELD, 'is_active', 
			'created_at', 'updated_at', 'first_name', 'last_name', 
			'password', 'company_name',)
		read_only_fields = ('is_active', 'created_at', 'updated_at',)

	def create(self, validated_data):
		company_name = validated_data.pop('company_name')
		user = User.objects.create(**validated_data)
		user.set_password(validated_data['password'])
		company, created = Company.objects.get_or_create(name=company_name)
		role = Role.objects.create(
			company=company,
			user=user,
			user_role='OW'
		)
		company.save()
		role.save()
		user.save()
		return user
