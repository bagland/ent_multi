from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from .models import Product, Sales, Arrival, Returns, SoldProduct, ArrivedProduct, ReturnedProduct, Company, Role
from .barcode import BarcodeDrawing
from random import randint

User = get_user_model()

class ProductSerializer(serializers.ModelSerializer):
	class Meta:
		model = Product
		fields = ('id', 'name', 'description', 'amount_left', 'wholesale_price', 'retail_price', 'barcode', 'vendor_name', 'manufacturer', 'company', 'had_no_barcode')
		read_only_fields = ('company', 'had_no_barcode')

class SoldProductSerializer(serializers.ModelSerializer):
	class Meta:
		model = SoldProduct
		fields = ('id', 'name', 'barcode', 'amount', 'retail_price', 'wholesale_price', 'sales', 'date',)
		read_only_fields = ('retail_price', 'wholesale_price', 'name', 'description', 'sales', 'date',)

class SalesSerializer(serializers.ModelSerializer):
	sold_products = SoldProductSerializer(many=True)
	class Meta:
		model = Sales
		fields = ('id', 'date', 'company', 'operator', 'sold_products')
		read_only_fields = ('company', 'operator', 'date')

	def create(self, validated_data):
		request = self.context.get('request', None)
		company = get_company(request)
		user = get_user(request)
		if request is None or request.user.is_anonymous():
			raise serializers.ValidationError("Must be logged in to make a sales.")
		products_data = validated_data.pop('sold_products')
		sales = Sales.objects.create(operator=user, company=company, date=timezone.now(), **validated_data)
		for product_data in products_data:
			amount = product_data['amount']
			barcode = product_data['barcode']
			product = Product.objects.get(barcode=barcode, company=company)
			product.amount_left -= Decimal(amount)
			product.save()
			SoldProduct.objects.create(
				sales=sales, 
				name=product.name,
				wholesale_price=product.wholesale_price, 
				retail_price=product.retail_price, 
				description=product.description, 
				**product_data
			)
		return sales

class ReturnedProductSerializer(serializers.ModelSerializer):
	class Meta:
		model = ReturnedProduct
		fields = ('id', 'name', 'barcode', 'amount', 'retail_price', 'wholesale_price', 'returns', 'date',)
		read_only_fields = ('retail_price', 'wholesale_price', 'name', 'description', 'returns', 'date',)

class ReturnsSerializer(serializers.ModelSerializer):
	returned_products = ReturnedProductSerializer(many=True)
	class Meta:
		model = Returns
		fields = ('id', 'date', 'company', 'operator', 'returned_products')
		read_only_fields = ('company', 'operator', 'date')

	def create(self, validated_data):
		request = self.context.get('request', None)
		company = get_company(request)
		user = get_user(request)
		products_data = validated_data.pop('returned_products')
		returns = Returns.objects.create(operator=user, company=company, date=timezone.now(), **validated_data)
		for product_data in products_data:
			amount = product_data['amount']
			barcode = product_data['barcode']
			product = Product.objects.get(barcode=barcode, company=company)
			product.amount_left  += Decimal(amount)
			product.save()
			ReturnedProduct.objects.create(
				returns=returns,
				name=product.name,
				wholesale_price=product.wholesale_price,
				retail_price=product.retail_price,
				description=product.description,
				**product_data
			)
		return returns

class ArrivedProductSerializer(serializers.ModelSerializer):
	class Meta:
		model = ArrivedProduct
		fields = ('id', 'name', 'description', 'barcode', 'amount', 'wholesale_price',
			'retail_price', 'vendor_name', 'manufacturer', 'arrival', 'date')
		read_only_fields = ('date',)

class ArrivalSerializer(serializers.ModelSerializer):
	arrived_products = ArrivedProductSerializer(many=True)
	class Meta:
		model = Arrival
		fields = ('id', 'date', 'company', 'operator', 'arrived_products')
		read_only_fields = ('company', 'operator', 'date')

	def create(self, validated_data):
		request = self.context.get('request', None)
		company = get_company(request)
		user = get_user(request)
		products_data = validated_data.pop('arrived_products')
		arrival = Arrival.objects.create(operator=user, company=company, date=timezone.now(), **validated_data)
		for product_data in products_data:
			name = product_data['name']
			barcode = product_data.pop('barcode', None)
			had_no_barcode = False
			if barcode is None:
				product = None
				try:
					barcode = randint(pow(10, 12), pow(10, 13) - 1)
					product = Product.objects.get(barcode=barcode, company=company)
				except Product.DoesNotExist:
					product = None
				while product is not None:
					try:
						barcode = randint(pow(10, 12), pow(10, 13) - 1)
						product = Product.objects.get(barcode=barcode, company=company)
					except Product.DoesNotExist:
						product = None
				had_no_barcode = True
			product, created = Product.objects.get_or_create(barcode=barcode, company=company, had_no_barcode=had_no_barcode)
			product.amount_left += product_data['amount']
			product.wholesale_price = product_data['wholesale_price']
			product.retail_price = product_data['retail_price']
			product.name = product_data['name']
			product.description = product_data.get('description', '')
			product.vendor_name = product_data.get('vendor_name', '')
			product.manufacturer = product_data.get('manufacturer', '')
			product.save()
			ArrivedProduct.objects.create(arrival=arrival, barcode=barcode, **product_data)
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

def get_company(request):
	if request is None and request.user.is_anonymous():
		raise serializers.ValidationError("Must be logged in to have an access.")
	role = Role.objects.get(user=request.user)
	return role.company

def get_user(request):
	if request is None and request.user.is_anonymous():
		raise serializers.ValidationError("Must be logged in to have an access.")
	return request.user