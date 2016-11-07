from rest_framework import permissions
from .models import Role

class IsPartOfCompany(permissions.BasePermission):
	def has_object_permission(self, request, view, obj):
		print('here')
		if request.user.is_anonymous():
			return False
		try:
			role = Role.objects.get(user=request.user)
			print(role.company)
			return role.company == obj.company
		except Role.DoesNotExist:
			return False