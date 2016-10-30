from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Product, Transaction, Arrival, SoldProduct

User = get_user_model()

class ProductSerializer(serializers.ModelSerializer):
	class Meta:
		model = Product
		fields = ('id', 'name', 'description', 'amount_left', 'retail_price', 'barcode', 'vendor_name', 'manufacturer')
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
		fields = ('id', 'date', 'sold_products')
		read_only_fields = ('id',)

class ArrivalSerializer(serializers.ModelSerializer):
	class Meta:
		model = Arrival
		fields = ('id', 'name', 'description', 'barcode', 'amount', 'wholesale_price', 'retail_price', 'date', 'owner')
		read_only_fields = ('owner', 'date')


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