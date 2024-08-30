from datetime import date, datetime, time
from datetime import timedelta
from unittest import result
from django.utils import timezone
from django.http import JsonResponse
from rest_framework import status
from rest_framework.views import APIView
from django.http import HttpResponse
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.authentication import SessionAuthentication, BasicAuthentication
# from django.core import serializers
from django.utils.html import escape
import html
from environ import Env
from backend.models import Admins, Menu
from backend.serializers import AdminSerializer, MenuSerializer
from django.contrib.auth.hashers import make_password, check_password
import jwt
from datetime import datetime, timedelta
from django.conf import settings
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q

from backend.models import FavorisRestaurant, FavorisMenu, Admins, Menu, Panier, PanierItem, Commande

env = Env()
env.read_env()

class AddMenuAPIView(APIView):
    def post(self, request):
        serializer = MenuSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UpdateMenuAPIView(APIView):
    def put(self, request, menu_id):
        try:
            menu = Menu.objects.get(id=menu_id)
        except Menu.DoesNotExist:
            return JsonResponse({"message": "Menu not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = MenuSerializer(menu, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeleteMenuAPIView(APIView):
    def delete(self, request, menu_id):
        try:
            menu = Menu.objects.get(id=menu_id)
            menu.delete()
            return JsonResponse({"message": "Menu deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Menu.DoesNotExist:
            return JsonResponse({"message": "Menu not found"}, status=status.HTTP_404_NOT_FOUND)
     
class GetAllMenusAPIView(APIView):
    def post(self, request):
        user_id = request.data.get('user_id')
        if not user_id:
            return JsonResponse({'message': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = Admins.objects.get(id=user_id, id_service=1)
        except Admins.DoesNotExist:
            return JsonResponse({'message': 'Invalid user ID'}, status=status.HTTP_404_NOT_FOUND)

        menus = Menu.objects.all()
        favoris_menus = FavorisMenu.objects.filter(user=user).values_list('menu_id', flat=True)
        favoris_restaurants = FavorisRestaurant.objects.filter(user=user).values_list('restaurant_id', flat=True)

        menu_data = []
        for menu in menus:
            menu_dict = {
                **MenuSerializer(menu).data,
                'is_favoris_menu': menu.id in favoris_menus,
                'is_favoris_restaurant': menu.id in favoris_restaurants
            }
            menu_data.append(menu_dict)

        return JsonResponse(menu_data, safe=False)

class MenuDetailAPIView(APIView):
    def get(self, request, menu_id):
        try:
            menu = Menu.objects.get(id=menu_id)
            serializer = MenuSerializer(menu)
            return JsonResponse(serializer.data, safe=False)
        except Menu.DoesNotExist:
            return JsonResponse({"message": "Menu not found"}, status=status.HTTP_404_NOT_FOUND)
