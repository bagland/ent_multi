from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Product, Transaction, Arrival

User = get_user_model()

class ProductSerializer(serializers.ModelSerializer):
	class Meta:
		model = Product
		fields = ('id', 'name', 'description', 'amount_left', 'retail_price', 'barcode', 'vendor_name', 'manufacturer')
		read_only_fields = ('owner',)

class TransactionSerializer(serializers.ModelSerializer):
	class Meta:
		model = Transaction
		fields = ('id', 'product_code', 'product_name', 'date', 'amount', 'total_price', 'owner')
		read_only_fields = ('id', 'date', 'product_name', 'total_price', 'owner')

class ArrivalSerializer(serializers.ModelSerializer):
	class Meta:
		model = Arrival
		fields = ('id', 'name', 'description', 'barcode', 'amount', 'wholesale_price', 'retail_price', 'date', 'owner')
		read_only_fields = ('owner', 'date')


class UserSerializer(serializers.ModelSerializer):
	full_name = serializers.CharField(source='get_full_name', read_only=True)

	class Meta:
		model = User
		fields = ('id', User.USERNAME_FIELD, 'password', 'full_name', 'is_active', 'email',)