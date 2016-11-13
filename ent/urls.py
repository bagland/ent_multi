from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'products', views.ProductViewSet)
router.register(r'sales', views.SalesViewSet)
router.register(r'users', views.UserViewSet)
router.register(r'arrivals', views.ArrivalViewSet)
router.register(r'returns', views.ReturnsViewSet)
router.register(r'returned_products', views.ReturnedProductViewSet)
router.register(r'sold_products', views.SoldProductViewSet)
router.register(r'arrived_products', views.ArrivedProductViewSet)