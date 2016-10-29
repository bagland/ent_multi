from django.db import models
from django.utils import timezone
from django.conf import settings
from decimal import Decimal

# Create your models here.
class Product(models.Model):
	name = models.CharField(max_length=100, default='')
	description = models.TextField(blank=True, default='')
	amount_left = models.DecimalField(default=0, max_digits=10, decimal_places=2)
	retail_price = models.IntegerField(default=0)
	barcode = models.CharField(unique=True, max_length=100)
	vendor_name = models.CharField(default='', max_length=100)
	manufacturer = models.CharField(default='', max_length=100)
	owner = models.ForeignKey(settings.AUTH_USER_MODEL, default=4)

	def __str__(self):
		return self.name

class Transaction(models.Model):
	product_code = models.CharField(max_length=100)
	date = models.DateTimeField(default=timezone.now)
	owner = models.ForeignKey(settings.AUTH_USER_MODEL, default=4)

	def __str__(self):
		return "{} at {}".format(self.product_name, self.date)

class SoldProduct(models.Model):
	name = models.CharField(max_length=100)
	description = models.TextField(blank=True, default='')
	barcode = models.CharField(max_length=100)
	amount = models.DecimalField(max_digits=10, decimal_places=2)
	retail_price = models.DecimalField(default=0, max_digits=10, decimal_places=2)
	wholesale_price = models.DecimalField(default=0, max_digits=10, decimal_places=2)
	transaction = models.ForeignKey(Transaction, related_name='sold_products')

class Arrival(models.Model):
	name = models.CharField(max_length=100, default='')
	description = models.TextField(blank=True, default='')
	barcode = models.CharField(max_length=100)
	amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	wholesale_price = models.DecimalField(default=0, max_digits=10, decimal_places=2)
	retail_price = models.IntegerField(default=0)
	date = models.DateTimeField(default=timezone.now)
	owner = models.ForeignKey(settings.AUTH_USER_MODEL, default=4)
	
	def __str__(self):
			return"{} at {}".format(self.name, self.date)