from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from decimal import Decimal
from datetime import date, time, datetime, timedelta
from django.views.generic.base import TemplateView

from .filters import SalesFilter, ArrivalFilter, ProductFilter, ReturnsFilter, ArrivedProductFilter, SoldProductFilter, ReturnedProductFilter
from rest_framework import authentication, permissions, viewsets, filters, status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authtoken.models import Token
from rest_framework.authentication import BasicAuthentication
from rest_framework.exceptions import PermissionDenied
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from .models import Product, Sales, Arrival, Returns, SoldProduct, ReturnedProduct, ArrivedProduct, Company, Role
from .serializers import ProductSerializer, SalesSerializer, UserSerializer, ArrivalSerializer, ReturnsSerializer, SoldProductSerializer, ReturnedProductSerializer, ArrivedProductSerializer
from django.template import loader, Context
from django.core.mail import EmailMultiAlternatives
from .permissions import IsPartOfCompany

User = get_user_model()

class DefaultsMixin(object):
	# authentication_classes = (
	# 	authentication.BasicAuthentication,
	# 	authentication.TokenAuthentication,
	# )
	permission_classes = (
		permissions.IsAuthenticated,
		IsPartOfCompany,
	)
	paginate_by = 25
	paginate_by_param = 'page_size'
	max_paginate_by = 100
	filter_backends = (
		filters.DjangoFilterBackend,
		filters.SearchFilter,
		filters.OrderingFilter,
	)

class ProductViewSet(DefaultsMixin, viewsets.ModelViewSet):
	"""
	Список товаров
	"""
	queryset = Product.objects.order_by('name')
	serializer_class = ProductSerializer
	search_fields = ('name', 'barcode', 'description',)
	lookup_field = 'barcode'
	filter_class = ProductFilter

	def list(self, request, *args, **kwargs):
		try:
			role = Role.objects.get(user=request.user)
			self.queryset = Product.objects.filter(company=role.company)
		except Role.DoesNotExist:
			# raise PermissionDenied('no products registered for a user')
			self.queryset = Product.objects.none()
		return super(ProductViewSet, self).list(request, *args, **kwargs)

class SalesViewSet(DefaultsMixin, viewsets.ModelViewSet):
	"""
	Продажа товара
	"""
	queryset = Sales.objects.order_by('date')
	serializer_class = SalesSerializer
	filter_class = SalesFilter
	search_fields = ('date',)

	def list(self, request, *args, **kwargs):
		try:
			role = Role.objects.get(user=request.user)
			self.queryset = Sales.objects.filter(company=role.company)
		except Role.DoesNotExist:
			# raise PermissionDenied('no products registered for a user')
			self.queryset = Sales.objects.none()
		return super(SalesViewSet, self).list(request, *args, **kwargs)

class SoldProductViewSet(DefaultsMixin, viewsets.ReadOnlyModelViewSet):
	queryset = SoldProduct.objects.order_by('date')
	serializer_class = SoldProductSerializer
	filter_class = SoldProductFilter
	search_fields = ('name', 'date',)

	def list(self, request, *args, **kwargs):
		try:
			role = Role.objects.get(user=request.user)
			self.queryset = SoldProduct.objects.filter(sales__company=role.company)
		except Role.DoesNotExist:
			# raise PermissionDenied('no products registered for a user')
			self.queryset = SoldProduct.objects.none()
		return super(SoldProductViewSet, self).list(request, *args, **kwargs)

class ReturnsViewSet(DefaultsMixin, viewsets.ModelViewSet):
	"""
	Возврат товара
	"""
	queryset = Returns.objects.order_by('date')
	serializer_class = ReturnsSerializer
	filter_class = ReturnsFilter
	search_fields = ('date',)

	def list(self, request, *args, **kwargs):
		try:
			role = Role.objects.get(user=request.user)
			self.queryset = Returns.objects.filter(company=role.company)
		except Role.DoesNotExist:
			# raise PermissionDenied('no products registered for a user')
			self.queryset = Returns.objects.none()
		return super(ReturnsViewSet, self).list(request, *args, **kwargs)

class ReturnedProductViewSet(DefaultsMixin, viewsets.ReadOnlyModelViewSet):
	queryset = ReturnedProduct.objects.order_by('date')
	serializer_class = ReturnedProductSerializer
	filter_class = ReturnedProductFilter
	search_fields = ('date',)

	def list(self, request, *args, **kwargs):
		try:
			role = Role.objects.get(user=request.user)
			self.queryset = ReturnedProduct.objects.filter(returns__company=role.company)
		except Role.DoesNotExist:
			# raise PermissionDenied('no products registered for a user')
			self.queryset = ReturnedProduct.objects.none()
		return super(ReturnedProductViewSet, self).list(request, *args, **kwargs)

class ArrivalViewSet(DefaultsMixin, viewsets.ModelViewSet):
	"""
	Приход товара
	"""
	queryset = Arrival.objects.order_by('date')
	serializer_class = ArrivalSerializer
	search_fields = ('date',)
	filter_class = ArrivalFilter
	ordering_fields = ('date',)

	def list(self, request, *args, **kwargs):
		try:
			role = Role.objects.get(user=request.user)
			self.queryset = Arrival.objects.filter(company=role.company)
		except Role.DoesNotExist:
			# raise PermissionDenied('no products registered for a user')
			self.queryset = Arrival.objects.none()
		return super(ArrivalViewSet, self).list(request, *args, **kwargs)

class ArrivedProductViewSet(DefaultsMixin, viewsets.ReadOnlyModelViewSet):
	queryset = ArrivedProduct.objects.order_by('date')
	serializer_class = ArrivedProductSerializer
	search_fields = ('name','date',)
	filter_class = ArrivedProductFilter
	ordering_fields = ('name','date',)

	def list(self, request, *args, **kwargs):
		try:
			role = Role.objects.get(user=request.user)
			self.queryset = ArrivedProduct.objects.filter(arrival__company=role.company)
		except Role.DoesNotExist:
			# raise PermissionDenied('no products registered for a user')
			self.queryset = ArrivedProduct.objects.none()
		return super(ArrivedProductViewSet, self).list(request, *args, **kwargs)

class UserViewSet(viewsets.ModelViewSet):
	# lookup_field = User.USERNAME_FIELD
	# lookup_url_kwarg = User.USERNAME_FIELD
	"""
	Создание пользователей
	"""
	queryset = User.objects.order_by(User.USERNAME_FIELD)
	serializer_class = UserSerializer

def index(request):
	print(settings.BASE_DIR)
	html = loader.get_template('index.html')
	html_content = html.render()
	return HttpResponse(html_content)

def send_summary_email():
	template = 'summary_email.html'
	today = datetime.now().date()
	tomorrow = today + timedelta(1)
	today_start = datetime.combine(today, time())
	today_end = datetime.combine(tomorrow, time())
	sales_list = Sales.objects.filter(date__gte=today_start).filter(date__lt=today_end)
	subject = 'Итоги за {}.{}.{}'.format(today.day, today.month, today.year)
	email = 'baglan.daribayev@gmail.com'
	plaintext = 'hi'
	html = loader.get_template(template)
	total = 0.0
	for sale in sales_list:
					total += sale.total_price

	data = Context({'transaction_list':sales_list, 'total':total})
	html_content = html.render(data)
	msg = EmailMultiAlternatives(subject, plaintext, 'apteka.sofiya@gmail.com', [email, 'sofi_kz@mail.ru'])
	msg.attach_alternative(html_content, "text/html")
	msg.send()
	return

def revenue(request):
	today = datetime.now().date()
	tomorrow = today + timedelta(1)
	today_start = datetime.combine(today, time())
	today_end = datetime.combine(tomorrow, time())
	sales_list = Sales.objects.filter(date__gte=today_start).filter(date__lt=today_end)
	total = 0.0
	for sale in sales_list:
			total += sale.total_price

	html = "<html><body>Today's revenue is {}</body></html>".format(total)
	return HttpResponse(html)

def month_revenue(request):
	today = datetime.now().date()
	sales_list = Sales.objects.filter(date__month=today.month).order_by('date')
	total = 0.0
	for sale in sales_list:
		total += sale.total_price

	html = "<html><body>This month's revenue is {}</body></html>".format(total)
	return HttpResponse(html)


def createAPIErrorJsonReponse(msg, code):
	return JsonResponse({'status': 'error',
												'reason': msg}, status=code)

def createAPISuccessJsonReponse(repDict):
	repDict['status'] = 'success'
	return JsonResponse(repDict)
