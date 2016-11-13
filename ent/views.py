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
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from .models import Product, Sales, Arrival, Returns, SoldProduct, ReturnedProduct, ArrivedProduct
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
		# IsPartOfCompany,
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

class SalesViewSet(DefaultsMixin, viewsets.ModelViewSet):
	"""
	Продажа товара
	"""
	queryset = Sales.objects.order_by('date')
	serializer_class = SalesSerializer
	filter_class = SalesFilter
	search_fields = ('date',)

class SoldProductViewSet(DefaultsMixin, viewsets.ReadOnlyModelViewSet):
	queryset = SoldProduct.objects.order_by('date')
	serializer_class = SoldProductSerializer
	filter_class = SoldProductFilter
	search_fields = ('name', 'date',)

class ReturnsViewSet(DefaultsMixin, viewsets.ModelViewSet):
	"""
	Возврат товара
	"""
	queryset = Returns.objects.order_by('date')
	serializer_class = ReturnsSerializer
	filter_class = ReturnsFilter
	search_fields = ('date',)

class ReturnedProductViewSet(DefaultsMixin, viewsets.ReadOnlyModelViewSet):
	queryset = ReturnedProduct.objects.order_by('date')
	serializer_class = ReturnedProductSerializer
	filter_class = ReturnedProductFilter
	search_fields = ('date',)

class ArrivalViewSet(DefaultsMixin, viewsets.ModelViewSet):
	"""
	Приход товара
	"""
	queryset = Arrival.objects.order_by('date')
	serializer_class = ArrivalSerializer
	search_fields = ('date',)
	filter_class = ArrivalFilter
	ordering_fields = ('date',)

class ArrivedProductViewSet(DefaultsMixin, viewsets.ReadOnlyModelViewSet):
	queryset = ArrivedProduct.objects.order_by('date')
	serializer_class = ArrivedProductSerializer
	search_fields = ('name','date',)
	filter_class = ArrivedProductFilter
	ordering_fields = ('name','date',)

	# def perform_create(self, serializer):
	# 	user = self.request.user
	# 	now = timezone.now()
	# 	name = self.request.data['name']
	# 	barcode = self.request.data['barcode']
	# 	amount = self.request.data['amount']
	# 	description = self.request.data['description']
	# 	retail_price = self.request.data['retail_price']
	# 	product, created = Product.objects.get_or_create(barcode=barcode, owner=user)
	# 	print(product)
	# 	if not amount:
	# 		amount = 0
	# 	if not retail_price:
	# 		retail_price = 0
	# 	product.amount_left += Decimal(amount)
	# 	product.retail_price = retail_price
	# 	product.name = name
	# 	product.description = description
	# 	product.save()
	# 	serializer.save(owner=user)
	# 	return createAPISuccessJsonReponse({})

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
