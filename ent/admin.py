from django.contrib import admin

# Register your models here.
from .models import Product

class ProductModelAdmin(admin.ModelAdmin):
	list_display = ('name', 'amount_left', 'retail_price', 'wholesale_price', 'barcode', 'company')
	list_filter = ['company']
	search_fields = ['name', 'barcode']
	class Meta:
		model = Product

admin.site.register(Product, ProductModelAdmin)
