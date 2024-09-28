# inventory/urls.py

from django.urls import path
from .views import *

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('items/', ItemListView.as_view(), name='item-list'),
    path('items/<int:item_id>/', ItemDetailView.as_view(), name='item-detail'),
]
