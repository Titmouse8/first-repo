from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('', views.index, name="index"),
    path('category/', views.CategoryView.as_view(), name='category'),
    path('menu-item/', views.MenuItemView.as_view(), name='menuitem'),
    path('menu-item/<int:product_id>', views.MenuItemSingleView.as_view(), name='menuitem-single'),
    path('order/', views.OrderView.as_view(), name='order'),
    path('user-order/', views.UserOrderView.as_view(), name='user-order'),
    path('order-item/', views.OrderItemView.as_view(), name='orderitem'),
    path('order-item/<int:pk>', views.OrderItemSingleView.as_view(), name='orderitem-single'),
    path('menu-item/info/', views.menuitem_info),
    path('api-token-auth/', obtain_auth_token),
]