from django.contrib import admin

# Register your models here.
from .models import Product, Role, Company

class ProductModelAdmin(admin.ModelAdmin):
	list_display = ('name', 'amount_left', 'retail_price', 'wholesale_price', 'barcode', 'company')
	list_filter = ['company']
	search_fields = ['name', 'barcode']
	actions_on_bottom = True

	class Meta:
		model = Product

	def get_queryset(self, request):
		qs = super(ProductModelAdmin, self).get_queryset(request)
		role = Role.objects.get(user=request.user)
		return qs.filter(company=role.company)
		if request.user.is_superuser:
			return qs
		role = Role.objects.get(user=request.user)
		return qs.filter(company=role.company)

admin.site.register(Product, ProductModelAdmin)
