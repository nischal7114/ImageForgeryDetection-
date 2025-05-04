from django.urls import path
from .import views
from .views import generate_pdf

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('upload/', views.image_upload, name='image_upload'),
    path('list/', views.image_list, name='image_list'),
    path('verify/', views.image_verification, name='image_verification'),
    path('detail/<int:image_id>/', views.image_detail, name='image_detail'),
    path('verify/<int:image_id>/', views.image_verification, name='image_verification'),
    path('images/verify/<int:image_id>/pdf/', generate_pdf, name='generate_pdf'),
    path('image/<int:image_id>/delete/', views.image_delete, name='image_delete'),
]