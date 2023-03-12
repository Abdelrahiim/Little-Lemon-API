from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth.models import User, Group
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from .models import MenuItem, Category, Cart, Order, OrderItem
from rest_framework.response import Response
from rest_framework import status
from .serializers import MenuItemSerializer, MangerListSerializer, CartSerializer, OrderSerializer, CartAddSerializer, \
    CartRemoveSerializer, SingleOrderSerializer, OrderPutSerializer, CategorySerializer
from .permissions import IsManger, IsDeliveryCrew
from rest_framework import viewsets
import math
from datetime import date


# Create your views here.

# ---------------------------------------------------------------
class MenuItemView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    ordering_fields = ['price', 'category']
    search_fields = ['Title', 'category__title']

    # ------------------------------
    def get_permissions(self):
        permission_classes = []
        if self.request.method != 'GET':
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]


# ---------------------------------------------------------------
class CategoryView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]


# ---------------------------------------------------------------
class MenuItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    # ------------------------------
    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.request.method == 'PATCH':
            permission_classes = [IsAuthenticated, IsManger | IsAdminUser]
        if self.request.method == "DELETE":
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]

    # ------------------------------
    def patch(self, request, *args, **kwargs):
        menuitem = MenuItem.objects.get(pk=self.kwargs['pk'])
        menuitem.featured = not menuitem.featured
        menuitem.save()
        return Response(
            {'message': 'Featured status of {} changed to {}'.format(str(menuitem.title), str(menuitem.featured))},
            status=status.HTTP_200_OK
        )


# ---------------------------------------------------------------
class ManagerView(viewsets.ModelViewSet):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = User.objects.filter(groups__name='Mangers')
    serializer_class = MangerListSerializer
    permission_classes = [IsAuthenticated, IsAdminUser | IsManger]

    # ------------------------------
    def create(self, request, *args, **kwargs):
        username = request.data['username']
        if username:
            user = get_object_or_404(User, username=username)
            manager = Group.objects.get(name='Mangers')
            manager.user_set.add(user)
        return Response({'Message': 'User added To Mangers Group'}, status=status.HTTP_201_CREATED)

    # ------------------------------
    def destroy(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        user = get_object_or_404(User, pk=pk)
        manager = Group.objects.get(name='Mangers')
        manager.user_set.remove(user)
        return Response({'message': 'User Remove From The Mangers Group'}, status=status.HTTP_200_OK)


# ---------------------------------------------------------------
class DeliveryCrewView(viewsets.ModelViewSet):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = User.objects.filter(groups__name='Delivery crew')
    serializer_class = MangerListSerializer
    permission_classes = [IsAuthenticated, IsAdminUser | IsManger]

    # ------------------------------
    def create(self, request, *args, **kwargs):
        username = request.data['username']
        if username:
            user = get_object_or_404(User, username=username)
            dcrew = Group.objects.get(name='Delivery crew')
            dcrew.user_set.add(user)
        return Response({"Message": "User Added To The Delivery Crew Group"}, status=status.HTTP_201_CREATED)

    # ------------------------------
    def destroy(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        user = get_object_or_404(User, pk=pk)
        dcrew = Group.objects.get(name='Delivery crew')
        dcrew.user_set.remove(user)
        return Response({"Message": "User Remove From The Delivery Crew Group"}, status=status.HTTP_200_OK)


# ---------------------------------------------------------------
class CartOperationsView(generics.ListCreateAPIView, generics.DestroyAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer

    # ------------------------------
    def get_queryset(self):
        cart = Cart.objects.filter(user=self.request.user)
        return cart

    # ------------------------------
    def post(self, request, *args, **kwargs):
        serialized_item = CartAddSerializer(data=request.data)
        serialized_item.is_valid(raise_exception=True)
        id = request.data['menuitem']
        quantity = request.data['quantity']
        item = get_object_or_404(MenuItem, id=id)
        price = int(quantity) * item.price
        try:
            Cart.objects.create(
                user=request.user, quantity=quantity,
                unitprice=item.price, price=price, menuitem_id=id)
        except:
            return Response({'message': 'Item is Already in The Item'}, status=status.HTTP_409_CONFLICT)
        return Response({'message': 'Item added to Cart'}, status=status.HTTP_201_CREATED)

    # ------------------------------
    def delete(self, request, *args, **kwargs):
        if self.request['menuitem']:
            serialized_item = CartRemoveSerializer(data=request.data)
            serialized_item.is_valid(raise_exception=True)
            menuitem = request.data['menuitem']
            cart = get_object_or_404(Cart, menuitem=menuitem, user=request.user)
            cart.delete()
            return Response({'message': 'Item Removed From Cart'}, status=status.HTTP_200_OK)
        else:
            Cart.objects.filter(user=request.user).delete()
            return Response({'message': 'All Item Removed From Cart'}, status=status.HTTP_201_CREATED)


# ---------------------------------------------------------------
class OrderOperationsView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = OrderSerializer

    # ------------------------------
    def get_queryset(self):
        if self.request.user.groups.filter(name='Managers').exists() or self.request.user.is_superuser == True:
            query = Order.objects.all()
        elif self.request.user.groups.filter(name='Delivery crew').exists():
            query = Order.objects.filter(delivery_crew=self.request.user)
        else:
            query = Order.objects.filter(user=self.request.user)
        return query

    # ------------------------------
    def get_permissions(self):
        if self.request.method == 'GET' or 'POST':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated, IsAdminUser | IsManger]
        return [permission() for permission in permission_classes]

    # ------------------------------
    def post(self, request, *args, **kwargs):
        cart = Cart.objects.filter(user = request.user)
        values = cart.values_list()
        if len(values) == 0:
            return Response({'message': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)
        total = math.fsum([float(value[-1]) for value in values])
        order = Order.objects.create(
            user=request.user, total=total,
            status=False, date=date.today())

        for i in cart.values():
            menuitem = get_object_or_404(MenuItem, id=i['menuitem'])
            orderitem = OrderItem.objects.create(
                order=order, menuitem=menuitem,
                quantity=i['quantity'], price=i['price'],
                unitprice=i['unitprice']
            )
            orderitem.save()
        cart.delete()
        return Response({'message': f'Your Order has been Placed Your Order Number is {order.id}'},
                        status=status.HTTP_201_CREATED)


# ---------------------------------------------------------------
class SingleOrderView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = SingleOrderSerializer

    # ------------------------------
    def get_permissions(self):
        order = Order.objects.get(pk=self.kwargs['pk'])
        if self.request.user == order.user or self.request.method == 'GET':
            permission_classes = [IsAuthenticated]
        elif self.request.method == 'PUT' or self.request.method == 'DELETE':
            permission_classes = [IsAuthenticated, IsAdminUser | IsManger]
        else:
            permission_classes = [IsAuthenticated, IsAdminUser | IsManger | IsDeliveryCrew]
        return [permission() for permission in permission_classes]

    # ------------------------------
    def get_queryset(self):
        query = OrderItem.objects.filter(order_id=self.kwargs['pk'])
        return query

    # ------------------------------
    def partial_update(self, request, *args, **kwargs):
        order = Order.objects.get(pk=self.kwargs['pk'])
        order.status = not order.status
        order.save()
        return Response(
            {'message': f'state of order #{order.id} changed to {order.status}'},
            status=status.HTTP_200_OK)

    # ------------------------------
    def update(self, request, *args, **kwargs):
        serialized_item = OrderPutSerializer(data=request.data)
        serialized_item.is_valid(raise_exception=True)
        order_pk = self.kwargs['pk']
        dcrew_pk = request.data['delivery_crew']
        order = get_object_or_404(Order, pk=order_pk)
        dcrew = get_object_or_404(User, pk=dcrew_pk)
        order.delivery_crew = dcrew
        order.save()
        return Response({'message': f'{dcrew.username} Was assigned to order #{order.id}'},
                        status=status.HTTP_201_CREATED)

    # ------------------------------
    def destroy(self, request, *args, **kwargs):
        order = Order.objects.get(pk=self.kwargs['pk'])
        order.delete()
        return Response({'message': f'order #{order.id} Was deleted Succefully '}, status=status.HTTP_200_OK)
