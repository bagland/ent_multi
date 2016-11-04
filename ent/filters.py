import django_filters
from .models import Sales, Arrival

class SalesFilter(django_filters.FilterSet):
	date = django_filters.DateFilter(name='date', lookup_type='contains')
	class Meta:
		model = Sales
		fields = ('date',)

class ArrivalFilter(django_filters.FilterSet):
	date_min = django_filters.DateFilter(name='date', lookup_type='gte')
	date_max = django_filters.DateFilter(name='date', lookup_type='lte')

	class Meta:
		model = Arrival
		fields = ('date_min', 'date_max',)
		