from django.db import models
from django.utils import timezone
from django.conf import settings
from decimal import Decimal
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin

class Company(models.Model):
	name = models.CharField(max_length=60, unique=True)

	def __str__(self):
		return self.name

class Product(models.Model):
	name = models.CharField(max_length=100, default='')
	description = models.TextField(blank=True, default='')
	amount_left = models.DecimalField(default=0, max_digits=10, decimal_places=2)
	retail_price = models.DecimalField(default=0, max_digits=10, decimal_places=2)
	wholesale_price = models.DecimalField(default=0, max_digits=10, decimal_places=2)
	barcode = models.CharField(max_length=100)
	vendor_name = models.CharField(default='', max_length=100)
	manufacturer = models.CharField(default='', max_length=100)
	company = models.ForeignKey(Company)
	had_no_barcode = models.BooleanField(default=False)

	unique_together = (('company', 'barcode'),)

	def __str__(self):
		return self.name

class Sales(models.Model):
	date = models.DateTimeField(default=timezone.now)
	company = models.ForeignKey(Company)
	operator = models.ForeignKey(settings.AUTH_USER_MODEL)

	def __str__(self):
		return "{}".format(self.date)

class SoldProduct(models.Model):
	name = models.CharField(max_length=100)
	description = models.TextField(blank=True)
	barcode = models.CharField(max_length=100)
	amount = models.DecimalField(max_digits=10, decimal_places=2)
	wholesale_price = models.DecimalField(max_digits=10, decimal_places=2)
	retail_price = models.DecimalField(max_digits=10, decimal_places=2)
	sales = models.ForeignKey(Sales, related_name='sold_products', blank=True)
	date = models.DateTimeField(default=timezone.now)

	def __str__(self):
		return self.name

class Returns(models.Model):
	date = models.DateTimeField(default=timezone.now)
	company = models.ForeignKey(Company)
	operator = models.ForeignKey(settings.AUTH_USER_MODEL)

	def __str__(self):
		return self.date

class ReturnedProduct(models.Model):
	name = models.CharField(max_length=100)
	description = models.TextField(blank=True)
	barcode = models.CharField(max_length=100)
	amount = models.DecimalField(max_digits=10, decimal_places=2)
	wholesale_price = models.DecimalField(max_digits=10, decimal_places=2)
	retail_price = models.DecimalField(max_digits=10, decimal_places=2)
	returns = models.ForeignKey(Returns, related_name='returned_products', blank=True)
	date = models.DateTimeField(default=timezone.now)

	def __str__(self):
		return self.name

class Arrival(models.Model):
	date = models.DateTimeField(default=timezone.now)
	company = models.ForeignKey(Company)
	operator = models.ForeignKey(settings.AUTH_USER_MODEL)

	def __str__(self):
		return "{}".format(self.date)

class ArrivedProduct(models.Model):
	name = models.CharField(max_length=100)
	description = models.TextField(blank=True, default='')
	barcode = models.CharField(blank=True, max_length=100)
	amount = models.DecimalField(max_digits=10, decimal_places=2)
	wholesale_price = models.DecimalField(default=0, max_digits=10, decimal_places=2)
	retail_price = models.DecimalField(default=0, max_digits=10, decimal_places=2)
	vendor_name = models.CharField(default='', max_length=100)
	manufacturer = models.CharField(default='', max_length=100)
	arrival = models.ForeignKey(Arrival, related_name='arrived_products', blank=True)
	date = models.DateTimeField(default=timezone.now)
	
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

class MyUser(AbstractBaseUser, PermissionsMixin):
	email = models.EmailField(
		verbose_name = 'email address',
		max_length = 255,
		unique = True,
	)

	first_name = models.CharField(max_length=40, blank=True)
	last_name = models.CharField(max_length=40, blank=True)
	is_active = models.BooleanField(default=True)
	is_admin = models.BooleanField(default=False)
	is_staff = models.BooleanField(default=False)

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

class Role(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	company = models.ForeignKey(Company)
	USER_TYPES = (
		('AD', 'Admin'),
		('OW', 'Owner'),
		('SE', 'Seller'),
	)
	user_role = models.CharField(max_length=2, choices=USER_TYPES, default='OW')
	last_updated = models.DateTimeField(auto_now=True)

	def __str__(self):
		return ' '.join([self.user.email, self.user_role, self.company.name])
