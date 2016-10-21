import django_filters
from .models import Transaction

class TransactionFilter(django_filters.FilterSet):
	date = django_filters.DateFilter(name='date', lookup_type='contains')
	class Meta:
		model = Transaction
		fields = ('date',)