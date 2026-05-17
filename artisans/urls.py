from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('artisans/', views.artisan_list, name='artisan_list'),
    path('artisans/create/', views.artisan_create, name='artisan_create'),
    path('artisans/<int:pk>/', views.artisan_detail, name='artisan_detail'),
    path('artisans/<int:pk>/edit/', views.artisan_edit, name='artisan_edit'),
    path('artisans/<int:pk>/delete/', views.artisan_delete, name='artisan_delete'),
    path('artisans/<int:artisan_pk>/material/create/', views.material_create, name='material_create'),
    path('material/<int:pk>/delete/', views.material_delete, name='material_delete'),
    path('artisans/<int:artisan_pk>/sale/create/', views.sale_create, name='sale_create'),
    path('sale/<int:pk>/delete/', views.sale_delete, name='sale_delete'),
]