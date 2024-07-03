from django.urls import path
from . import views
from .views import check_active_key

urlpatterns = [
    path('', views.home, name='home'),
    path('revoke/<int:key_id>/', views.revoke_key_view, name='revoke_key'),
    path('request_key/', views.request_key, name='request_key'),
    path('check_active_key/', check_active_key, name='check_active_key'),
]
