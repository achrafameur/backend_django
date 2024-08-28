from django.shortcuts import render
# Create your views here.
from backend.models import FavorisRestaurant, FavorisMenu, Admins, Menu, Panier, PanierItem, Commande
from backend.serializers import MenuSerializer, FavorisRestaurantSerializer, FavorisMenuSerializer, PanierItemSerializer, PanierSerializer
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import status
import uuid

# Gestion des restaurants favoris
class AddFavorisRestaurantAPIView(APIView):
    def post(self, request):
        utilisateur_id = request.data.get('user_id')
        restaurant_id = request.data.get('restaurant_id')
        
        if not utilisateur_id or not restaurant_id:
            return JsonResponse({'message': 'User ID and Restaurant ID are required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            restaurant = Admins.objects.get(id=restaurant_id, id_service=2)
        except Admins.DoesNotExist:
            return JsonResponse({'message': 'Invalid restaurant ID'}, status=status.HTTP_404_NOT_FOUND)
        user = Admins.objects.filter(id=utilisateur_id, id_service=1).first()
        if not user:
            return JsonResponse({'message': 'Invalid user ID'}, status=status.HTTP_404_NOT_FOUND)
        # Vérifiez si le restaurant est déjà dans les favoris
        favoris, created = FavorisRestaurant.objects.get_or_create(user=user, restaurant=restaurant)
        if not created:
            return JsonResponse({'message': 'Restaurant already in favorites'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = FavorisRestaurantSerializer(favoris)
        return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
    
class DeleteFavorisRestaurantAPIView(APIView):
    def delete(self, request, restaurant_id):
        utilisateur_id = request.data.get('user_id')
        if not utilisateur_id:
            return JsonResponse({'message': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = Admins.objects.get(id=utilisateur_id, id_service=1)
        except Admins.DoesNotExist:
            return JsonResponse({'message': 'Invalid user ID'}, status=status.HTTP_404_NOT_FOUND)
        try:
            favoris = FavorisRestaurant.objects.get(user=user, restaurant_id=restaurant_id)
            favoris.delete()
            return JsonResponse({'message': 'Favorite restaurant deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except FavorisRestaurant.DoesNotExist:
            return JsonResponse({'message': 'Favorite restaurant not found'}, status=status.HTTP_404_NOT_FOUND)

class GetAllFavorisRestaurantsAPIView(APIView):
    def get(self, request):
        utilisateur_id = request.query_params.get('user_id')
        if not utilisateur_id:
            return JsonResponse({'message': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = Admins.objects.get(id=utilisateur_id, id_service=1)
        except Admins.DoesNotExist:
            return JsonResponse({'message': 'Invalid user ID'}, status=status.HTTP_404_NOT_FOUND)
        
        favoris_restaurants = FavorisRestaurant.objects.filter(user=user)
        restaurant_ids = favoris_restaurants.values_list('restaurant_id', flat=True)
        
        restaurants = Menu.objects.filter(id__in=restaurant_ids)
        serializer = MenuSerializer(restaurants, many=True)
        
        return JsonResponse(serializer.data, safe=False)


# Gestion des menus favoris     
class AddFavorisMenuAPIView(APIView):
    def post(self, request):
        utilisateur_id = request.data.get('user_id')
        menu_id = request.data.get('menu_id')
        if not utilisateur_id or not menu_id:
            return JsonResponse({'message': 'User ID and Menu ID are required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            menu = Menu.objects.get(id=menu_id)
        except Menu.DoesNotExist:
            return JsonResponse({'message': 'Invalid menu ID'}, status=status.HTTP_404_NOT_FOUND)
        user = Admins.objects.filter(id=utilisateur_id, id_service=1).first()
        if not user:
            return JsonResponse({'message': 'Invalid user ID'}, status=status.HTTP_404_NOT_FOUND)
        # Vérifiez si le menu est déjà dans les favoris
        favoris, created = FavorisMenu.objects.get_or_create(user=user, menu=menu)
        if not created:
            return JsonResponse({'message': 'Menu already in favorites'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = FavorisMenuSerializer(favoris)
        return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
    
class DeleteFavorisMenuAPIView(APIView):
    def delete(self, request, menu_id):
        utilisateur_id = request.data.get('user_id')
        if not utilisateur_id:
            return JsonResponse({'message': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = Admins.objects.get(id=utilisateur_id, id_service=1)
        except Admins.DoesNotExist:
            return JsonResponse({'message': 'Invalid user ID'}, status=status.HTTP_404_NOT_FOUND)
        try:
            favoris = FavorisMenu.objects.get(user=user, menu_id=menu_id)
            favoris.delete()
            return JsonResponse({'message': 'Favorite menu deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except FavorisMenu.DoesNotExist:
            return JsonResponse({'message': 'Favorite menu not found'}, status=status.HTTP_404_NOT_FOUND)

class GetAllFavorisMenusAPIView(APIView):
    def get(self, request):
        utilisateur_id = request.query_params.get('user_id')
        if not utilisateur_id:
            return JsonResponse({'message': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = Admins.objects.get(id=utilisateur_id, id_service=1)
        except Admins.DoesNotExist:
            return JsonResponse({'message': 'Invalid user ID'}, status=status.HTTP_404_NOT_FOUND)
        
        favoris_menus = FavorisMenu.objects.filter(user=user)
        menu_ids = favoris_menus.values_list('menu_id', flat=True)
        
        menus = Menu.objects.filter(id__in=menu_ids)
        serializer = MenuSerializer(menus, many=True)
        
        return JsonResponse(serializer.data, safe=False)

    
# Gestion du Panier
class AddToPanierAPIView(APIView):
    def post(self, request):
        utilisateur_id = request.data.get('user_id')
        menu_id = request.data.get('menu_id')
        quantite = request.data.get('quantite', 1)
        if not utilisateur_id or not menu_id:
            return JsonResponse({'error': 'User ID and Menu ID are required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            utilisateur = Admins.objects.get(id=utilisateur_id, id_service=1)
        except Admins.DoesNotExist:
            return JsonResponse({'error': 'Invalid User ID or User is not a client'}, status=status.HTTP_404_NOT_FOUND)
        try:
            menu = Menu.objects.get(id=menu_id)
        except Menu.DoesNotExist:
            return JsonResponse({"error": "Menu not found"}, status=status.HTTP_404_NOT_FOUND)
        panier, created = Panier.objects.get_or_create(utilisateur=utilisateur)
        item, created = PanierItem.objects.get_or_create(panier=panier, menu=menu)
        # Set the quantity to the value provided in the request
        item.quantite = int(quantite)
        item.save()
        serializer = PanierItemSerializer(item)
        return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
    
class UpdatePanierItemAPIView(APIView):
    def put(self, request, item_id):
        quantite = request.data.get('quantite')
        if quantite is None:
            return JsonResponse({"error": "Quantity is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            item = PanierItem.objects.get(id=item_id)
            item.quantite = int(quantite)
            item.save()
            serializer = PanierItemSerializer(item)
            return JsonResponse(serializer.data)
        except PanierItem.DoesNotExist:
            return JsonResponse({"error": "Panier item not found"}, status=status.HTTP_404_NOT_FOUND)
    
class DeletePanierItemAPIView(APIView):
    def delete(self, request, item_id):
        try:
            item = PanierItem.objects.get(id=item_id)
            item.delete()
            return JsonResponse({"message": "Item deleted"}, status=status.HTTP_204_NO_CONTENT)
        except PanierItem.DoesNotExist:
            return JsonResponse({"error": "Panier item not found"}, status=status.HTTP_404_NOT_FOUND)

class GetPanierAPIView(APIView):
    def get(self, request):
        utilisateur_id = request.query_params.get('user_id')
        if not utilisateur_id:
            return JsonResponse({"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            utilisateur = Admins.objects.get(id=utilisateur_id, id_service=1)
        except Admins.DoesNotExist:
            return JsonResponse({'error': 'Invalid User ID or User is not a client'}, status=status.HTTP_404_NOT_FOUND)
        try:
            panier = Panier.objects.get(utilisateur=utilisateur)
            panier_items = panier.items.all()
            serializer = PanierItemSerializer(panier_items, many=True)
            return JsonResponse(serializer.data, safe=False)
        except Panier.DoesNotExist:
            return JsonResponse({"error": "Panier not found"}, status=status.HTTP_404_NOT_FOUND)

class ValidatePanierAPIView(APIView):
    def post(self, request):
        utilisateur_id = request.data.get('user_id')
        if not utilisateur_id:
            return JsonResponse({"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            utilisateur = Admins.objects.get(id=utilisateur_id, id_service=1)
        except Admins.DoesNotExist:
            return JsonResponse({'error': 'Invalid User ID or User is not a client'}, status=status.HTTP_404_NOT_FOUND)
        try:
            panier = Panier.objects.get(utilisateur=utilisateur)
            if not panier.items.exists():
                return JsonResponse({"error": "Panier is empty"}, status=status.HTTP_400_BAD_REQUEST)
            total = sum(item.total() for item in panier.items.all())
            reference = str(uuid.uuid4())
            commande = Commande.objects.create(
                utilisateur=utilisateur,
                panier=panier,
                reference=reference,
                montant_total=total,
                est_payee=False
            )
            return JsonResponse({"reference": reference, "montant_total": total}, status=status.HTTP_201_CREATED)
        except Panier.DoesNotExist:
            return JsonResponse({"error": "Panier not found"}, status=status.HTTP_404_NOT_FOUND)
