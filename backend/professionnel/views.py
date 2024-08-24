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

env = Env()
env.read_env()

class AddMenuAPIView(APIView):
    # authentication_classes = [CustomAuthentication]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = MenuSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UpdateMenuAPIView(APIView):
    # authentication_classes = [CustomAuthentication]

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
    # authentication_classes = [CustomAuthentication]

    def delete(self, request, menu_id):
        try:
            menu = Menu.objects.get(id=menu_id)
            menu.delete()
            return JsonResponse({"message": "Menu deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Menu.DoesNotExist:
            return JsonResponse({"message": "Menu not found"}, status=status.HTTP_404_NOT_FOUND)
     
class GetAllMenusAPIView(APIView):
    # authentication_classes = [CustomAuthentication]

    def get(self, request):
        menus = Menu.objects.all()
        serializer = MenuSerializer(menus, many=True)
        return JsonResponse(serializer.data, safe=False)
    
class MenuDetailAPIView(APIView):
    def get(self, request, menu_id):
        try:
            menu = Menu.objects.get(id=menu_id)
            serializer = MenuSerializer(menu)
            return JsonResponse(serializer.data, safe=False)
        except Menu.DoesNotExist:
            return JsonResponse({"message": "Menu not found"}, status=status.HTTP_404_NOT_FOUND)
