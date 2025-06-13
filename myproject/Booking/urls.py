from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('category/', views.CategoryView.as_view(), name='category'),
    path('menu-item/', views.MenuItemView.as_view(), name='menuitem'),
    path('menu-item/<int:pk>', views.MenuItemSingleView.as_view(), name='menuitem-single'),
    path('order-item/<int:pk>', views.OrderItemView.as_view(), name='orderitem'),
    path('order/', views.OrderView.as_view(), name='order'),
]