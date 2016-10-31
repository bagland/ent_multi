from django.db import models
from django.utils import timezone
from django.conf import settings
from decimal import Decimal
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser

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
	date = models.DateTimeField(default=timezone.now)
	owner = models.ForeignKey(settings.AUTH_USER_MODEL, default=4)

	def __str__(self):
		return "{}".format(self.date)

class SoldProduct(models.Model):
	name = models.CharField(max_length=100)
	description = models.TextField(blank=True)
	barcode = models.CharField(max_length=100)
	amount = models.DecimalField(max_digits=10, decimal_places=2)
	wholesale_price = models.DecimalField(max_digits=10, decimal_places=2)
	retail_price = models.IntegerField()
	transaction = models.ForeignKey(Transaction, related_name='sold_products', blank=True)

	def __str__(self):
		return self.name

class Arrival(models.Model):
	date = models.DateTimeField(default=timezone.now)
	owner = models.ForeignKey(settings.AUTH_USER_MODEL, default=4)

	def __str__(self):
		return "{}".format(self.date)

class ArrivedProduct(models.Model):
	name = models.CharField(max_length=100)
	description = models.TextField(blank=True, default='')
	barcode = models.CharField(max_length=100)
	amount = models.DecimalField(max_digits=10, decimal_places=2)
	wholesale_price = models.DecimalField(default=0, max_digits=10, decimal_places=2)
	retail_price = models.IntegerField(default=0)
	vendor_name = models.CharField(default='', max_length=100)
	manufacturer = models.CharField(default='', max_length=100)
	arrival = models.ForeignKey(Arrival, related_name='arrived_products', blank=True)
	
	def __str__(self):
		return self.name

class MyUserManager(BaseUserManager):
	def create_user(self, email, password=None):
		if not email:
			raise ValueError('Users must have an email address')

		user = self.model(email=self.normalize_email(email),)
		user.set_password(password)
		user.save()
		return user

	def create_superuser(self, email, password):
		user = self.create_user(email, password=password,)
		user.is_admin = True
		user.save()
		return user

class MyUser(AbstractBaseUser):
	email = models.EmailField(
		verbose_name = 'email address',
		max_length = 255,
		unique = True,
	)

	first_name = models.CharField(max_length=40, blank=True)
	last_name = models.CharField(max_length=40, blank=True)
	is_active = models.BooleanField(default=True)
	is_admin = models.BooleanField(default=False)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	objects = MyUserManager()

	USERNAME_FIELD = 'email'

	def get_full_name(self):
		return ' '.join([self.last_name, self.first_name])

	def get_short_name(self):
		return self.email

	def __str__(self):
		return self.email
