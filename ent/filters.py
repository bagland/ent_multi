import django_filters
from .models import Sales, Arrival, Product, Returns
from datetime import timedelta

class SalesFilter(django_filters.FilterSet):
	date_min = django_filters.DateFilter(name='date', lookup_type='gte')
	date_max = django_filters.DateFilter(name='date', method='filter_date_max')

	def filter_date_max(self, queryset, name, value):
		return queryset.filter(date__lt=value+timedelta(1))

	class Meta:
		model = Sales
		fields = ('date_min', 'date_max',)

class ReturnsFilter(django_filters.FilterSet):
	date_min = django_filters.DateFilter(name='date', lookup_type='gte')
	date_max = django_filters.DateFilter(name='date', lookup_type='filter_date_max')

	def filter_date_max(self, queryset, name, value):
		return queryset.filter(date__lt=value+timedelta(1))

	class Meta:
		model = Returns
		fields = ('date_min', 'date_max',)

class ArrivalFilter(django_filters.FilterSet):
	date_min = django_filters.DateFilter(name='date', lookup_type='gte')
	date_max = django_filters.DateFilter(name='date', method='filter_date_max')

	def filter_date_max(self, queryset, name, value):
		return queryset.filter(date__lt=value+timedelta(1))

	class Meta:
		model = Arrival
		fields = ('date_min', 'date_max',)
		
class ProductFilter(django_filters.FilterSet):
	name = django_filters.CharFilter(name='name', lookup_type='contains')
	barcode = django_filters.CharFilter(name='barcode', lookup_type='contains')
	description = django_filters.CharFilter(name='description', lookup_type='contains')
	class Meta:
		model = Product
		fields = ('name', 'barcode', 'description',)