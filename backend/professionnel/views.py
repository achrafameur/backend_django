from django.utils import timezone
from django.http import JsonResponse
from rest_framework import status
from rest_framework.views import APIView
from environ import Env
from backend.models import Admins, Menu
from backend.serializers import AdminSerializer, MenuSerializer, MenuAddSerializer, RestaurantSeatsSerializer, MenuUpdateSerializer
from django.utils import timezone
from django.db.models import Sum, F
from backend.models import FavorisRestaurant, FavorisMenu, Admins, Menu, Panier, PanierItem, Commande, RestaurantSeats
from decimal import Decimal, ROUND_HALF_UP
from venv import logger
from django.db.models import Q
from datetime import datetime
import pytz
from django.utils.dateformat import format as django_format

env = Env()
env.read_env()

class AddMenuAPIView(APIView):
    def post(self, request):
        serializer = MenuAddSerializer(data=request.data)
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
        
        serializer = MenuUpdateSerializer(menu, data=request.data, partial=True)
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
        search_query = request.data.get('search_query', '')

        if not user_id:
            return JsonResponse({'message': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = Admins.objects.get(id=user_id, id_service=1)
        except Admins.DoesNotExist:
            return JsonResponse({'message': 'Invalid user ID'}, status=status.HTTP_404_NOT_FOUND)

        menus = Menu.objects.filter(number_dispo__gt=0)
        if search_query:
            menus = menus.filter(Q(nom__icontains=search_query) | Q(admin__nom_organisme__icontains=search_query))

        favoris_menus = FavorisMenu.objects.filter(user=user).values_list('menu_id', flat=True)
        favoris_restaurants = FavorisRestaurant.objects.filter(user=user).values_list('restaurant_id', flat=True)

        menu_data = []
        for menu in menus:
            menu_dict = {
                **MenuSerializer(menu).data,
                'is_favoris_menu': menu.id in favoris_menus,
                'is_favoris_restaurant': menu.admin.id in favoris_restaurants
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
        

import pytz

class RestaurantOrdersAPIView(APIView):
    def get(self, request, restaurant_id):
        try:
            restaurant = Admins.objects.get(id=restaurant_id, id_service=2)
            menus = Menu.objects.filter(admin=restaurant)
            
            panier_items = PanierItem.objects.filter(menu__in=menus, est_payee=True).select_related('panier', 'menu', 'panier__utilisateur')
            
            commandes_dict = {}
            france_timezone = pytz.timezone('Europe/Paris')

            for item in panier_items:
                commande = item.panier.commande
                commande_ref = commande.reference

                if commande_ref not in commandes_dict:
                    date_commande_local = commande.date_commande.astimezone(france_timezone)

                    commandes_dict[commande_ref] = {
                        "commande_reference": commande_ref,
                        "date_commande": date_commande_local,
                        "prenom_client": item.panier.utilisateur.prenom,
                        "nom_client": item.panier.utilisateur.nom,
                        "menus": [],
                        "total_commande": 0
                    }

                commandes_dict[commande_ref]["menus"].append({
                    "menu_nom": item.menu.nom,
                    "quantite": item.quantite,
                    "prix_unitaire": str(item.menu.prix),
                    "total": str(item.total())
                })

                commandes_dict[commande_ref]["total_commande"] += item.total()

            orders_data = list(commandes_dict.values())

            orders_data.sort(key=lambda x: x["date_commande"], reverse=True)

            for order in orders_data:
                order["date_commande"] = django_format(order["date_commande"], 'Y-m-d H:i:s')

            return JsonResponse({"orders": orders_data}, status=status.HTTP_200_OK)

        except Admins.DoesNotExist:
            return JsonResponse({"error": "Restaurant not found"}, status=status.HTTP_404_NOT_FOUND)



class RestaurantStatsAPIView(APIView):
    def get(self, request, restaurant_id):
        today = timezone.now().date()
        start_of_month = today.replace(day=1)
        start_of_year = today.replace(month=1, day=1)

        try:
            # All orders stats
            total_orders = PanierItem.objects.filter(menu__admin_id=restaurant_id, est_payee=True).values('panier_id').distinct().count()
            total_revenue = PanierItem.objects.filter(menu__admin_id=restaurant_id, est_payee=True).aggregate(Sum('menu__prix'))['menu__prix__sum'] or Decimal('0.00')
            restaurant_share = total_revenue * Decimal('0.85')
            restaurant_share = restaurant_share.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            # Today's orders stats
            today_orders = PanierItem.objects.filter(menu__admin_id=restaurant_id, est_payee=True, panier__commande__date_commande__date=today).count()
            today_revenue = PanierItem.objects.filter(menu__admin_id=restaurant_id, est_payee=True, panier__commande__date_commande__date=today).aggregate(Sum('menu__prix'))['menu__prix__sum'] or Decimal('0.00')

            # Monthly and Annual stats
            monthly_revenue = PanierItem.objects.filter(
                menu__admin_id=restaurant_id,
                est_payee=True,
                panier__commande__date_commande__date__range=[start_of_month, today]
            ).aggregate(Sum('menu__prix'))['menu__prix__sum'] or Decimal('0.00')

            annual_revenue = PanierItem.objects.filter(
                menu__admin_id=restaurant_id,
                est_payee=True,
                panier__commande__date_commande__date__range=[start_of_year, today]
            ).aggregate(Sum('menu__prix'))['menu__prix__sum'] or Decimal('0.00')

            stats_data = {
                "total_orders": total_orders,
                "total_revenue": str(total_revenue),
                "restaurant_share": str(restaurant_share),
                "today_orders": today_orders,
                "today_revenue": str(today_revenue),
                "monthly_revenue": str(monthly_revenue),
                "annual_revenue": str(annual_revenue)
            }

            return JsonResponse({"stats": stats_data}, status=status.HTTP_200_OK)

        except Menu.DoesNotExist:
            return JsonResponse({'error': 'Invalid restaurant ID'}, status=status.HTTP_404_NOT_FOUND)
        
class VerifyProfessionalAPIView(APIView):
    def get(self, request, admin_id):
        try:
            admin = Admins.objects.get(id=admin_id, id_service=2)
        except Admins.DoesNotExist:
            return JsonResponse({'error': 'Admin not found'}, status=status.HTTP_404_NOT_FOUND)

        if admin.is_verified:
            logger.debug("Le professionnel est déjà vérifié.")
            return JsonResponse({'status': 'already_verified', 'message': 'Le professionnel est déjà vérifié.'})

        admin.is_verified = True
        admin.save()
        logger.debug("Le professionnel a été vérifié avec succès.")
        
        return JsonResponse({'status': 'success', 'message': 'Le professionnel a été vérifié avec succès.'}, status=status.HTTP_200_OK)
    


class DeclineProfessionalAPIView(APIView):
    def get(self, request, admin_id):

        if not admin_id:
            return JsonResponse({'error': 'Admin ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            admin = Admins.objects.get(id=admin_id, id_service=2, is_verified=0)
        except Admins.DoesNotExist:
            return JsonResponse({'error': 'Admin not found'}, status=status.HTTP_404_NOT_FOUND)

        if admin.is_declined:
            logger.debug("Le professionnel est déjà refusé.")
            return JsonResponse({'status': 'already_declined', 'message': 'Le professionnel est déjà refusé.'})

        admin.is_declined = True
        admin.save()
        logger.debug("Le professionnel a été refusé avec succès.")
        
        return JsonResponse({'status': 'success', 'message': 'Le professionnel a été refusé avec succès.'}, status=status.HTTP_200_OK)
    

class ActivateProfessionalAPIView(APIView):
    def get(self, request, admin_id):
        try:
            admin = Admins.objects.get(id=admin_id, id_service=2)
        except Admins.DoesNotExist:
            return JsonResponse({'error': 'Admin not found'}, status=status.HTTP_404_NOT_FOUND)

        if admin.is_verified:
            return JsonResponse({'status': 'already_verified', 'message': 'Le professionnel est déjà vérifié.'})

        admin.is_verified = True
        admin.is_declined = False
        admin.save()
        
        return JsonResponse({'status': 'success', 'message': 'Le professionnel a été vérifié avec succès.'}, status=status.HTTP_200_OK)
    


class DesactivateProfessionalAPIView(APIView):
    def get(self, request, admin_id):

        if not admin_id:
            return JsonResponse({'error': 'Admin ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            admin = Admins.objects.get(id=admin_id, id_service=2)
        except Admins.DoesNotExist:
            return JsonResponse({'error': 'Admin not found'}, status=status.HTTP_404_NOT_FOUND)

        if admin.is_declined:
            return JsonResponse({'status': 'already_declined', 'message': 'Le professionnel est déjà refusé.'})

        admin.is_declined = True
        admin.is_verified = False
        admin.save()
        
        return JsonResponse({'status': 'success', 'message': 'Le professionnel a été refusé avec succès.'}, status=status.HTTP_200_OK)

class GetListOfProfToVerify(APIView):
    def get(self, request):
        professionnels = Admins.objects.filter(id_service=2, is_verified=False, is_declined=False)
        serializer = AdminSerializer(professionnels, many=True)
        return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)
    
class GetRestaurantByIdAPIView(APIView):
    def get(self, request, restaurant_id):
        try:
            restaurant = Admins.objects.get(id=restaurant_id, id_service=2)
        except Admins.DoesNotExist:
            return JsonResponse({"detail": "Restaurant not found."}, status=status.HTTP_404_NOT_FOUND)

        restaurant_data = {
            'id': restaurant.id,
            'nom': restaurant.nom,
            'prenom': restaurant.prenom,
            'nom_organisme': restaurant.nom_organisme,
            'num_siret': restaurant.num_siret,
            'adresse_mail': restaurant.adresse_mail,
            'localisation': restaurant.localisation,
            'latitude': restaurant.latitude,
            'longitude': restaurant.longitude,
            'is_verified': restaurant.is_verified
        }

        menus = Menu.objects.filter(admin=restaurant)
        menu_data = []
        for menu in menus:
            menu_data.append({
                'id': menu.id,
                'nom': menu.nom,
                'description': menu.description,
                'image': menu.image.url if menu.image else None,
                'prix': str(menu.prix),
                'number_dispo': menu.number_dispo
            })

        restaurant_data['menus'] = menu_data

        return JsonResponse(restaurant_data, status=status.HTTP_200_OK)

class GetAvailableSeatsAPIView(APIView):
    def post(self, request):
        user_id = request.data.get('user_id')

        if not user_id:
            return JsonResponse({'message': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = Admins.objects.get(id=user_id, id_service=2)
        except Admins.DoesNotExist:
            return JsonResponse({'message': 'Invalid restaurant ID'}, status=status.HTTP_404_NOT_FOUND)

        try:
            seats = RestaurantSeats.objects.get(restaurant=user)
        except RestaurantSeats.DoesNotExist:
            return JsonResponse({'message': 'No seat data available for this restaurant'}, status=status.HTTP_404_NOT_FOUND)

        seat_data = RestaurantSeatsSerializer(seats).data

        return JsonResponse(seat_data, safe=False)

# class UpdateAvailableSeatsAPIView(APIView):
#     def put(self, request, restaurant_id):
#         try:
#             seats = RestaurantSeats.objects.get(restaurant_id=restaurant_id)
#         except RestaurantSeats.DoesNotExist:
#             return JsonResponse({"message": "RestaurantSeats not found"}, status=status.HTTP_404_NOT_FOUND)
        
#         serializer = RestaurantSeatsSerializer(seats, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return JsonResponse(serializer.data)
#         return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UpdateAvailableSeatsAPIView(APIView):
    def put(self, request, restaurant_id):
        try:
            seats = RestaurantSeats.objects.get(restaurant_id=restaurant_id)
        except RestaurantSeats.DoesNotExist:
            return JsonResponse({"message": "RestaurantSeats not found"}, status=status.HTTP_404_NOT_FOUND)
        
        data = request.data.copy()
        if 'number_dispo' in data:
            data['available_seats'] = data.pop('number_dispo')
        
        serializer = RestaurantSeatsSerializer(seats, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
