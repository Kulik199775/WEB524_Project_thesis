"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path, include

from django.conf.urls.static import static
from django.views.generic import TemplateView, RedirectView

urlpatterns = [
                  path('accounts/login/', RedirectView.as_view(url='/users/login/', permanent=True)),
                  path('accounts/', include('django.contrib.auth.urls')),

                  path("admin/", admin.site.urls),
                  path('', include('catalog.urls', namespace='catalog')),
                  path('users/', include('users.urls')),
                  path('cart/', include('cart.urls')),
                  path('reviews/', include('reviews.urls')),
                  path('orders/', include('orders.urls')),
                  path('privacy-policy/', TemplateView.as_view(template_name='pages/privacy_policy.html'),
                       name='privacy_policy'),
                  path('delivery/', TemplateView.as_view(template_name='pages/delivery.html'), name='delivery'),
                  path('about/', TemplateView.as_view(template_name='pages/about.html'), name='about')
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
