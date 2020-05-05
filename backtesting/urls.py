from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('example1/', views.ex1, name='ex1'),
    path('example2/', views.ex2, name='ex2'),
]
