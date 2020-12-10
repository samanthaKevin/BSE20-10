from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('sales-report/', views.salesreport, name='salesreport'),
    path('/admin/login/?next=/', auth_views.login_required),
]