from django.urls import path
from .views import MenuItemView, CategoryView, MenuItemDetailView, ManagerView, DeliveryCrewView, CartOperationsView, \
    OrderOperationsView, SingleOrderView

urlpatterns = [
    path('menu-items/', MenuItemView.as_view()),
    path('menu-items/category/', CategoryView.as_view()),
    path('menu-items/<int:pk>', MenuItemDetailView.as_view()),
    path('groups/managers/users/', ManagerView.as_view({'get': 'list', 'post': 'create'})),
    path('groups/managers/users/<int:pk>', ManagerView.as_view({'delete': 'destroy', 'get': 'list'})),
    path('groups/delivery-crew/users/', DeliveryCrewView.as_view({'get': 'list', 'post': 'create'})),
    path('groups/delivery-crew/users/<int:pk>', DeliveryCrewView.as_view({'delete': 'destroy', 'get': 'list'})),
    path('cart/menu-item/', CartOperationsView.as_view()),
    path('orders/', OrderOperationsView.as_view()),
    path('orders/<int:pk>', SingleOrderView.as_view())
]
