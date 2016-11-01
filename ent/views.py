from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from decimal import Decimal
from datetime import date, time, datetime, timedelta
from django.views.generic.base import TemplateView

from .filters import TransactionFilter, ArrivalFilter
from rest_framework import authentication, permissions, viewsets, filters, status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authtoken.models import Token
from rest_framework.authentication import BasicAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from .models import Product, Transaction, Arrival
from .serializers import ProductSerializer, TransactionSerializer, UserSerializer, ArrivalSerializer
from django.template import loader, Context
from django.core.mail import EmailMultiAlternatives
from .permissions import IsOwnerOrReadOnly

User = get_user_model()

class DefaultsMixin(object):
	# authentication_classes = (
	# 	authentication.BasicAuthentication,
	# 	authentication.TokenAuthentication,
	# )
	permission_classes = (
		permissions.IsAuthenticated,
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
	search_fields = ('name',)
	lookup_field = 'barcode'

class TransactionViewSet(DefaultsMixin, viewsets.ModelViewSet):
	"""
	Продажа товара
	"""
	queryset = Transaction.objects.order_by('date')
	serializer_class = TransactionSerializer
	filter_class = TransactionFilter
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

def send_summary_email():
	template = 'summary_email.html'
	today = datetime.now().date()
	tomorrow = today + timedelta(1)
	today_start = datetime.combine(today, time())
	today_end = datetime.combine(tomorrow, time())
	transaction_list = Transaction.objects.filter(date__gte=today_start).filter(date__lt=today_end)
	subject = 'Итоги за {}.{}.{}'.format(today.day, today.month, today.year)
	email = 'baglan.daribayev@gmail.com'
	plaintext = 'hi'
	html = loader.get_template(template)
	total = 0.0
	for transaction in transaction_list:
					total += transaction.total_price

	data = Context({'transaction_list':transaction_list, 'total':total})
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
	transaction_list = Transaction.objects.filter(date__gte=today_start).filter(date__lt=today_end)
	total = 0.0
	for transaction in transaction_list:
			total += transaction.total_price

	html = "<html><body>Today's revenue is {}</body></html>".format(total)
	return HttpResponse(html)

def month_revenue(request):
	today = datetime.now().date()
	transaction_list = Transaction.objects.filter(date__month=today.month).order_by('date')
	total = 0.0
	for transaction in transaction_list:
		total += transaction.total_price

	html = "<html><body>This month's revenue is {}</body></html>".format(total)
	return HttpResponse(html)


def createAPIErrorJsonReponse(msg, code):
	return JsonResponse({'status': 'error',
												'reason': msg}, status=code)

def createAPISuccessJsonReponse(repDict):
	repDict['status'] = 'success'
	return JsonResponse(repDict)
