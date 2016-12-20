from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from decimal import Decimal
from datetime import date, time, datetime, timedelta
from django.views.generic.base import TemplateView
import os
from generate_barcode import BarcodePage
from django.contrib.auth.decorators import login_required

from .filters import SalesFilter, ArrivalFilter, ProductFilter, ReturnsFilter, ArrivedProductFilter, SoldProductFilter, ReturnedProductFilter
from rest_framework import authentication, permissions, viewsets, filters, status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authtoken.models import Token
from rest_framework.authentication import BasicAuthentication
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from .models import Product, Sales, Arrival, Returns, SoldProduct, ReturnedProduct, ArrivedProduct, Company, Role
from .serializers import ProductSerializer, SalesSerializer, UserSerializer, ArrivalSerializer, ReturnsSerializer, SoldProductSerializer, ReturnedProductSerializer, ArrivedProductSerializer
from django.template import loader, Context
from django.core.mail import EmailMultiAlternatives
from .permissions import IsPartOfCompany

User = get_user_model()

class TurnoverPagination(LimitOffsetPagination):
	def get_paginated_response(self, data):
		return Response({
			'count': self.count,
			'next': self.get_next_link(),
			'previous': self.get_previous_link(),
			'total_products': self.total_products,
			'total_sum': self.total_sum,
			'results': data
		})

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

class TurnoverMixin(DefaultsMixin):
	pagination_class = TurnoverPagination
	object_class = None
	def list(self, request, *args, **kwargs):
		if self.pagination_class is not None:
			self._paginator = self.pagination_class()
		self._paginator.total_products, self._paginator.total_sum = 0, 0
		try:
			role = Role.objects.get(user=request.user)
			date_min = request.query_params.get('date_min', None)
			date_max = request.query_params.get('date_max', None)
			self._paginator.total_products, self._paginator.total_sum = self.get_total_products_and_sum(date_min, date_max)
			self.queryset = self.queryset.filter(company=role.company)
		except Role.DoesNotExist:
			self.queryset = self.serializer_class.Meta.model.objects.none()
		return super().list(request, *args, **kwargs)

	def get_total_products_and_sum(self, date_min, date_max):
		object_set = None
		if date_min is not None:
			object_set = self.object_class.objects.filter(date__gte=date_min)
		if date_max is not None:
			formatted_date_max = datetime.strptime(date_max, '%Y-%m-%d')
			if object_set is None:
				object_set = self.object_class.objects.filter(date__lte=formatted_date_max+timedelta(1))
			else:
				object_set = object_set.filter(date__lte=formatted_date_max+timedelta(1))
		if object_set is None:
			object_set = self.object_class.objects.all()
		total_sum = 0.0
		for product in object_set:
			total_price = product.retail_price * product.amount
			total_sum += float(total_price)
		return object_set.count(), total_sum

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

class SalesViewSet(TurnoverMixin, viewsets.ModelViewSet):
	"""
	Продажа товара
	"""
	object_class = SoldProduct
	queryset = Sales.objects.order_by('date')
	serializer_class = SalesSerializer
	filter_class = SalesFilter
	search_fields = ('date',)

	def destroy(self, request, *args, **kwargs):
		user = request.user
		role = Role.objects.get(user=user)
		sales = Sales.objects.get(id=int(self.kwargs['pk']))
		if sales.company == role.company:
			sold_products = SoldProduct.objects.filter(sales=sales)
			for sold_product in sold_products:
				product = Product.objects.get(barcode=sold_product.barcode)
				product.amount_left += sold_product.amount
				product.save()
				sold_product.delete()
			return super(SalesViewSet, self).destroy(request, *args, **kwargs)
		else:
			createAPIErrorJsonReponse('Unauthorized.', 401)

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

class ReturnsViewSet(TurnoverMixin, viewsets.ModelViewSet):
	"""
	Возврат товара
	"""
	object_class = ReturnedProduct
	queryset = Returns.objects.order_by('date')
	serializer_class = ReturnsSerializer
	filter_class = ReturnsFilter
	search_fields = ('date',)

	def destroy(self, request, *args, **kwargs):
		user = request.user
		role = Role.objects.get(user=user)
		returns = Returns.objects.get(id=int(self.kwargs['pk']))
		if returns.company == role.company:
			returned_products = ReturnedProduct.objects.filter(returns=returns)
			for returned_product in returned_products:
				product = Product.objects.get(barcode=sold_product.barcode)
				product.amount_left -= returned_product.amount
				product.save()
				returned_product.delete()
			return super(ReturnsViewSet, self).destroy(request, *args, **kwargs)
		else:
			createAPIErrorJsonReponse('Unauthorized.', 401)

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

class ArrivalViewSet(TurnoverMixin, viewsets.ModelViewSet):
	"""
	Приход товара
	"""
	object_class = ArrivedProduct
	queryset = Arrival.objects.order_by('date')
	serializer_class = ArrivalSerializer
	search_fields = ('date',)
	filter_class = ArrivalFilter
	ordering_fields = ('date',)

	def destroy(self, request, *args, **kwargs):
		user = request.user
		role = Role.objects.get(user=user)
		arrival = Arrival.objects.get(id=int(self.kwargs['pk']))
		if arrival.company == role.company:
			arrived_products = ArrivedProduct.objects.filter(arrival=arrival)
			for arrived_product in arrived_products:
				product = Product.objects.get(barcode=arrived_product.barcode)
				product.amount_left -= arrived_product.amount
				product.save()
				arrived_product.delete()
			return super(ArrivalViewSet, self).destroy(request, *args, **kwargs)
		else:
			createAPIErrorJsonReponse('Unauthorized.', 401)

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

@login_required
def get_pdf(request):
	print(request.user)
	try:
		role = Role.objects.get(user=request.user)
	except Role.DoesNotExist:
		return HttpResponse('No role found!')
	barcodePage = BarcodePage(role.company)
	test_file = open(os.path.join(settings.BASE_DIR, 'new.pdf'), 'rb')
	response = HttpResponse(content=test_file)
	response['Content-Type'] = 'application/pdf'
	response['Content-Disposition'] = 'attachment; filename="%s.pdf"' \
									  % 'whatever'
	return response

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
