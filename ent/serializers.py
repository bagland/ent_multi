from rest_framework import serializers
from django.contrib.auth import get_user_model
from decimal import Decimal
from .models import Product, Transaction, Arrival, SoldProduct, ArrivedProduct

User = get_user_model()

class ProductSerializer(serializers.ModelSerializer):
	class Meta:
		model = Product
		fields = ('id', 'name', 'description', 'amount_left', 'retail_price', 'barcode', 'vendor_name', 'manufacturer', 'owner')
		read_only_fields = ('owner',)

class SoldProductSerializer(serializers.ModelSerializer):
	class Meta:
		model = SoldProduct
		fields = ('id', 'name', 'description', 'barcode', 'amount', 'retail_price', 'wholesale_price', 'transaction')
		read_only_fields = ('retail_price', 'wholesale_price', 'name', 'description', 'transaction')

class TransactionSerializer(serializers.ModelSerializer):
	sold_products = SoldProductSerializer(many=True)
	class Meta:
		model = Transaction
		fields = ('id', 'date', 'owner', 'sold_products')
		read_only_fields = ('owner',)

	def create(self, validated_data):
		request = self.context.get('request', None)
		if request is None and request.user.is_anonymous():
			raise serializers.ValidationError("Must be logged in to make a transaction.")
		products_data = validated_data.pop('sold_products')
		transaction = Transaction.objects.create(**validated_data)
		transaction(owner=request.user)
		transaction(date=timezone.now())
		transaction.save()
		for product_data in products_data:
			amount = product_data['amount']
			barcode = product_data['barcode']
			product = Product.objects.get(barcode=barcode)
			product.amount_left -= Decimal(amount)
			product.save()
			SoldProduct.objects.create(transaction=transaction, **product_data)
		return transaction

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
		read_only_fields = ('owner',)

	def create(self, validated_data):
		request = self.context.get('request', None)
		if request is None and request.user.is_anonymous():
			raise serializers.ValidationError("Must be logged in to make an arrival.")
		products_data = validated_data.pop('arrived_products')
		arrival = Arrival.objects.create(**validated_data)
		arrival(owner = request.user)
		arrival(date=timezone.now())
		arrival.save()
		for product_data in products_data:
			barcode = product_data['barcode']
			product, created = Product.objects.get_or_create(barcode=barcode)
			if created:
				product.amount_left += product_data['amount']
				product.wholesale_price = product_data['wholesale_price']
				product.retail_price = product_data['retail_price']
				product.name = product_data['name']
				product.description = product_data['description']
				product.vendor_name = product_data['vendor_name']
				product.manufacturer = product_data['manufacturer']

			ArrivedProduct.objects.create(arrival=arrival, **product_data)
		return arrival

class UserSerializer(serializers.ModelSerializer):
	password = serializers.CharField(write_only=True, required=False)

	class Meta:
		model = User
		fields = ('id', User.USERNAME_FIELD, 'is_active', 
			'created_at', 'updated_at', 'first_name', 'last_name', 
			'password',)
		read_only_fields = ('is_active', 'created_at', 'updated_at',)

	def create(self, validated_data):
		user = User.objects.create(**validated_data)
		user.set_password(validated_data['password'])
		user.save()
		return user