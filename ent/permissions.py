from rest_framework.permissions import BasePermission
from .models import Role

class IsPartOfCompany(BasePermission):
	def has_object_permission(self, request, view, obj):
		# return False
		# print('here')
		try:
			role = Role.objects.get(user=request.user)
			return role.company == obj.company
		except Role.DoesNotExist:
			return False