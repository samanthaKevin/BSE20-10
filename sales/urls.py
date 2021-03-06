from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('sales-report/', views.salesreport, name='salesreport'),
    path('expense-report/', views.expensereport, name='expensereport'),
    path('admin/login/?next=/', auth_views.login_required),
    path('accounts/logout', auth_views.LogoutView, name='logout'),
    path('weather/', views.weather, name='weather'),
    path('prices/', views.prices, name='prices'),
    path('riskassessment/', views.riskassessment, name='riskassessment'),
    path('importExpense/', views.importExpenseCSV, name='importExpense'),
    path('importIncome/', views.importIncomeCSV, name='importIncome'),
    path('predictPrice/', views.predictPrice, name='predictPrice'),
    path('predictWeather/', views.predict, name='predictWeather'),
]