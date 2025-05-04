from django.urls import path
from . import views

urlpatterns = [
    path('', views.case_list, name='case_list'),
    path('create/', views.case_create, name='case_create'),
    path('<int:pk>/edit/', views.case_update, name='case_update'),
    path('<int:pk>/delete/', views.case_delete, name='case_delete'),
    path('<int:case_id>/', views.case_detail, name='case_detail'),
]
