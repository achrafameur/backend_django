from django.shortcuts import render
# Create your views here.
from backend.models import FavorisRestaurant, FavorisMenu, Admins, Menu, Panier, PanierItem, Commande, Litige, RestaurantSeats
from backend.serializers import MenuSerializer,LitigeSerializer, FavorisRestaurantSerializer, FavorisMenuSerializer, PanierItemSerializer, AdminSerializer
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import status
import uuid
import stripe
from django.conf import settings
from django.http import HttpResponse
import logging
logger = logging.getLogger(__name__)
from django.shortcuts import get_object_or_404
from math import radians, cos, sin, asin, sqrt

stripe.api_key = settings.STRIPE_SECRET_KEY

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

        # Check if the restaurant is already in the user's favorites
        favoris, created = FavorisRestaurant.objects.get_or_create(user=user, restaurant=restaurant)
        if not created:
            return JsonResponse({'message': 'Restaurant already in favorites'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = FavorisRestaurantSerializer(favoris)
        return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)

class DeleteFavorisRestaurantAPIView(APIView):
    def delete(self, request, restaurant_id):
        utilisateur_id = request.data.get('user_id')
        print(restaurant_id)
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
    def post(self, request):
        utilisateur_id = request.data.get('user_id')
        print(utilisateur_id)
        if not utilisateur_id:
            return JsonResponse({'message': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = Admins.objects.get(id=utilisateur_id, id_service=1)
        except Admins.DoesNotExist:
            return JsonResponse({'message': 'Invalid user ID'}, status=status.HTTP_404_NOT_FOUND)
        
        favoris_restaurants = FavorisRestaurant.objects.filter(user_id=utilisateur_id)
        print(favoris_restaurants)
        restaurant_ids = favoris_restaurants.values_list('restaurant_id', flat=True)
        print(restaurant_ids)
        restaurants = Admins.objects.filter(id__in=restaurant_ids, id_service=2)
        serializer = AdminSerializer(restaurants, many=True)
        
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
        
        panier, created = Panier.objects.get_or_create(utilisateur=utilisateur, etat='en_cours')
        if not created and panier.etat == 'valide':
            # Créer un nouveau panier si le panier actuel est déjà validé
            panier = Panier.objects.create(utilisateur=utilisateur)

        item, created = PanierItem.objects.get_or_create(panier=panier, menu=menu)
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

# class GetPanierAPIView(APIView):
#     def get(self, request):
#         utilisateur_id = request.query_params.get('user_id')
#         if not utilisateur_id:
#             return JsonResponse({"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)
#         try:
#             utilisateur = Admins.objects.get(id=utilisateur_id, id_service=1)
#         except Admins.DoesNotExist:
#             return JsonResponse({'error': 'Invalid User ID or User is not a client'}, status=status.HTTP_404_NOT_FOUND)
#         try:
#             panier = Panier.objects.get(utilisateur=utilisateur, etat='en_cours')
#             panier_items = panier.items.all()
#             serializer = PanierItemSerializer(panier_items, many=True)
#             return JsonResponse(serializer.data, safe=False)
#         except Panier.DoesNotExist:
#             return JsonResponse({"error": "Panier not found"}, status=status.HTTP_404_NOT_FOUND)

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
            panier = Panier.objects.get(utilisateur=utilisateur, etat='en_cours')
            panier_items = panier.items.all()
            
            total_panier = sum(float(item.menu.prix) * item.quantite for item in panier_items)

            reserved_restaurants = set(item.menu.admin.id for item in panier_items if item.sur_place)

            total_tables = len(reserved_restaurants) * 3
            fees = 1
            total = total_panier + len(reserved_restaurants) * 3 + fees
            
            serializer = PanierItemSerializer(panier_items, many=True)
            
            response_data = {
                'panier_id': panier.id,
                'items': serializer.data,
                'total_panier': total_panier,
                'total_tables': total_tables,
                "fees" : fees,
                'total': total
            }
            return JsonResponse(response_data, safe=False)
        
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
            panier = Panier.objects.get(utilisateur=utilisateur, etat = 'en_cours')
            if panier.etat == 'valide':
                return JsonResponse({"error": "This panier is already validated."}, status=status.HTTP_400_BAD_REQUEST)
            
            items = panier.items.filter(est_payee=False)
            if not items.exists():
                return JsonResponse({"error": "Panier is empty or all items are paid"}, status=status.HTTP_400_BAD_REQUEST)

            # total = sum(item.total() for item in items)
            total_panier = sum(float(item.menu.prix) * item.quantite for item in items)

            reserved_restaurants = set(item.menu.admin.id for item in items if item.sur_place)
            total_tables = len(reserved_restaurants) * 3
            fees = 1
            total = total_panier + len(reserved_restaurants) * 3 + fees
            reference = str(uuid.uuid4())

            # Créer la commande
            commande = Commande.objects.create(
                utilisateur=utilisateur,
                panier=panier,
                reference=reference,
                montant_total=total,
                est_payee=False
            )

            # Mettre à jour l'état du panier
            panier.etat = 'valide'
            panier.save()

            return JsonResponse({
                "reference": reference, 
                "montant_total": total,
                "fees": fees,
                "total_tables": total_tables,
                "items": [{
                    "id": item.id,
                    "nom": item.menu.nom,
                    "quantite": item.quantite
                } for item in items]
            }, status=status.HTTP_201_CREATED)
        
        except Panier.DoesNotExist:
            return JsonResponse({"error": "Panier not found"}, status=status.HTTP_404_NOT_FOUND)


class CreateCheckoutSessionAPIView(APIView):
    def post(self, request):
        try:
            reference = request.data.get('reference')
            if not reference:
                return JsonResponse({"error": "Reference is required"}, status=400)
            
            commande = Commande.objects.get(reference=reference)
            
            # Créer une session de paiement Stripe
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': 'eur',
                            'product_data': {
                                'name': f"Commande {commande.reference}",
                            },
                            'unit_amount': int(commande.montant_total * 100),
                        },
                        'quantity': 1,
                    },
                ],
                mode='payment',
                success_url="http://localhost:3000/commandes",
                cancel_url="http://localhost:3000/cancel",
                client_reference_id=reference, 
            )
            
            # Retourner l'URL de la session Stripe
            return JsonResponse({"url": checkout_session.url})
        
        except Commande.DoesNotExist:
            return JsonResponse({"error": "Commande not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
        
class StripeWebhookView(APIView):
    def post(self, request):

        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

        if not sig_header:
            return HttpResponse("Missing signature header", status=400)

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        except ValueError as e:
            return HttpResponse("Invalid payload", status=400)
        except stripe.error.SignatureVerificationError as e:
            return HttpResponse("Invalid signature", status=400)

        # Handle the event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            client_reference_id = session.get('client_reference_id')

            if not client_reference_id:
                return HttpResponse("client_reference_id is None", status=400)

            try:
                commande = Commande.objects.get(reference=client_reference_id)
                commande.est_payee = True
                commande.save()

                for item in commande.panier.items.all():
                    item.est_payee = True
                    item.save()
                
                menu = item.menu
                if menu.number_dispo >= item.quantite:
                    menu.number_dispo -= item.quantite
                    menu.save()
                else:
                    return HttpResponse(f"Not enough stock for menu {menu.nom}", status=400)
                
                if item.sur_place:
                        try:
                            restaurant_seats = RestaurantSeats.objects.get(restaurant=menu.admin)
                            if restaurant_seats.available_seats >= 1:
                                restaurant_seats.available_seats -= 1
                                restaurant_seats.save()
                            else:
                                return HttpResponse(f"No available seats for restaurant {menu.admin.nom}", status=400)
                        except RestaurantSeats.DoesNotExist:
                            return HttpResponse(f"RestaurantSeats for restaurant {menu.admin.nom} not found", status=404)

            except Commande.DoesNotExist:
                return HttpResponse(f"Commande with reference {client_reference_id} does not exist.", status=404)

        return HttpResponse(status=200)
    

class UserOrdersAPIView(APIView):
    def get(self, request, user_id):
        try:
            utilisateur = Admins.objects.get(id=user_id, id_service=1)
            commandes = Commande.objects.filter(utilisateur=utilisateur).select_related('panier').prefetch_related('panier__items__menu')

            orders_data = []
            for commande in commandes:
                items_data = []
                # Accessing items via the reverse relation 'items' on the Panier model
                for item in commande.panier.items.all():
                    try:
                        menu_name = item.menu.nom
                        menu_price = item.menu.prix
                        item_total = item.total()
                    except PanierItem.menu.RelatedObjectDoesNotExist:
                        menu_name = "Menu not available"
                        menu_price = 0
                        item_total = 0

                    items_data.append({
                        "id": item.id,
                        "nom": menu_name,
                        "quantite": item.quantite,
                        "prix": menu_price,
                        "total": item_total,
                    })

                orders_data.append({
                    "reference": commande.reference,
                    "date_commande": commande.date_commande,
                    "montant_total": commande.montant_total,
                    "est_payee": commande.est_payee,
                    "items": items_data
                })

            return JsonResponse({"commandes": orders_data}, status=status.HTTP_200_OK)
        
        except Admins.DoesNotExist:
            return JsonResponse({'error': 'Invalid User ID or User is not a client'}, status=status.HTTP_404_NOT_FOUND)
        except Commande.DoesNotExist:
            return JsonResponse({'error': 'No orders found for this user'}, status=status.HTTP_404_NOT_FOUND)


class LitigeListAPIView(APIView):
    def get(self, request):
        litiges = Litige.objects.all()
        serializer = LitigeSerializer(litiges, many=True)
        return JsonResponse(serializer.data, safe=False , status=status.HTTP_200_OK)
    
class LitigeCreateAPIView(APIView):
    def post(self, request):
        serializer = LitigeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LitigeDetailAPIView(APIView):
    def get_object(self, litige_id):
        return get_object_or_404(Litige, id=litige_id)

    def get(self, request, litige_id):
        litige = self.get_object(litige_id)
        serializer = LitigeSerializer(litige)
        return JsonResponse(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, litige_id):
        litige = self.get_object(litige_id)
        serializer = LitigeSerializer(litige, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, litige_id):
        litige = self.get_object(litige_id)
        litige.delete()
        return JsonResponse({"message": "Litige deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

        
def calculate_distance(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1 
    dlon = lon2 - lon1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371
    return c * r

class GetNearbyRestaurantsAPIView(APIView):
    def post(self, request):
        client_id = request.data.get('client_id')
        # Récupère le client
        client = get_object_or_404(Admins, id=client_id)
        client_lat = client.latitude
        client_lon = client.longitude

        if not client_lat or not client_lon:
            return JsonResponse({"error": "Client location not available"}, status=status.HTTP_400_BAD_REQUEST)

        # Récupère tous les restaurants vérifiés
        restaurants = Admins.objects.filter(id_service=2, is_verified=True)

        nearby_restaurants = []
        for restaurant in restaurants:
            if restaurant.latitude and restaurant.longitude:
                distance = calculate_distance(client_lat, client_lon, restaurant.latitude, restaurant.longitude)
                if distance <= 10:
                    nearby_restaurants.append({
                        'id': restaurant.id,
                        'nom_organisme': restaurant.nom_organisme,
                        'distance': distance,
                        'latitude': restaurant.latitude,
                        'longitude': restaurant.longitude
                    })

        return JsonResponse(nearby_restaurants, safe=False, status=status.HTTP_200_OK)
    
class ReserveTableAPIView(APIView):
    def post(self, request):
        admin_id = request.data.get('admin_id')
        panier_id = request.data.get('panier_id')
        print(admin_id)

        if not admin_id or not panier_id:
            return JsonResponse({"error": "Admin ID and Panier ID are required"}, status=status.HTTP_400_BAD_REQUEST)

        restaurant = get_object_or_404(Admins, id=admin_id, id_service=2)
        print(restaurant)
        panier = get_object_or_404(Panier, id=panier_id, etat='en_cours')
        print(restaurant)
        items = PanierItem.objects.filter(panier=panier, menu__admin=restaurant)
        if not items.exists():
            return JsonResponse({"error": "No items found for this panier and restaurant"}, status=status.HTTP_404_NOT_FOUND)
        
        items.update(sur_place=True)
        return JsonResponse({"success": "Items marked as reserved"}, status=status.HTTP_200_OK)
    

class CancelReservationAPIView(APIView):
    def post(self, request):
        admin_id = request.data.get('admin_id')
        panier_id = request.data.get('panier_id')

        if not admin_id or not panier_id:
            return JsonResponse({"error": "Admin ID and Panier ID are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the restaurant exists
        restaurant = get_object_or_404(Admins, id=admin_id, id_service=2)

        # Get the panier
        panier = get_object_or_404(Panier, id=panier_id, utilisateur__id_service=1, etat='en_cours')

        # Update items
        items = PanierItem.objects.filter(panier=panier, menu__admin=restaurant)
        if not items.exists():
            return JsonResponse({"error": "No items found for this panier and restaurant"}, status=status.HTTP_404_NOT_FOUND)
        
        items.update(sur_place=False)
        return JsonResponse({"success": "Reservation canceled"}, status=status.HTTP_200_OK)