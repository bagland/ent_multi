"""enterprise URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework_swagger.views import get_swagger_view
from ent.urls import router
from ent.views import ProductViewSet
from ent import views

add_items = ProductViewSet.as_view({
    'post': 'add_items',
})

schema_view = get_swagger_view(title='Enterprise API')

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api-token-auth/', views.UserTokenAPIView.as_view()),
    url(r'^api/', include(router.urls)),
    url(r'^revenue/', views.revenue),
    url(r'^month_revenue/', views.month_revenue),
    url(r'^$',  views.index, name='index'),
    url(r'^pdf/', views.get_pdf),
    url(r'^api/docs/', schema_view),
    url(r'^accounts/login/$', auth_views.login, {'template_name': 'admin/login.html'}),
    url(r'^accounts/logout/$', auth_views.logout)
]
