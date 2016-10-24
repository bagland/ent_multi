import django_filters
from .models import Transaction, Arrival

class TransactionFilter(django_filters.FilterSet):
	date = django_filters.DateFilter(name='date', lookup_type='contains')
	class Meta:
		model = Transaction
		fields = ('date',)

class ArrivalFilter(django_filters.FilterSet):
	date_min = django_filters.DateFilter(name='date', lookup_type='gte')
	date_max = django_filters.DateFilter(name='date', lookup_type='lte')

	class Meta:
		model = Arrival
		fields = ('date_min', 'date_max',)
		