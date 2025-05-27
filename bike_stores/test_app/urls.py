from django.urls import path
from . import  views

urlpatterns = [
    path('index/', views.index, name='index'),
    path('test_json_res', views.test_json_res, name='test_json_res'),
]