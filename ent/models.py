from django.db import models
from django.utils import timezone
from django.conf import settings

# Create your models here.
class Product(models.Model):
	name = models.CharField(max_length=100, default='')
	description = models.TextField(blank=True, default='')
	amount_left = models.DecimalField(default=0, max_digits=4, decimal_places=1)
	retail_price = models.IntegerField()
	barcode = models.CharField(unique=True, max_length=100)
	vendor_name = models.CharField(default='', max_length=100)
	manufacturer = models.CharField(default='', max_length=100)
	owner = models.ForeignKey(settings.AUTH_USER_MODEL, default=4)

	def __str__(self):
		return self.name

class Transaction(models.Model):
	product_code = models.CharField(max_length=100)
	product_name = models.CharField(max_length=100, default='')
	total_price = models.IntegerField()
	date = models.DateTimeField(default=timezone.now)
	amount = models.DecimalField(max_digits=4, decimal_places=1)
	owner = models.ForeignKey(settings.AUTH_USER_MODEL, default=4)

	def __str__(self):
		return "{} at {}".format(self.product_name, self.date)