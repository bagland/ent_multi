from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'products', views.ProductViewSet)
router.register(r'transactions', views.TransactionViewSet)
router.register(r'users', views.UserViewSet)
router.register(r'arrivals', views.ArrivalViewSet)