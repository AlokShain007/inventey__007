from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                "user": {
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "ResponseMessage": "Regestration done successfully",
                },
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response({"Respone_errror":serializer.errors,"ResponseMessage" :"Something went wrong"} ,status=status.HTTP_400_BAD_REQUEST)

# User Login View (JWT Token)
class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]


class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            # Get the token from the request
            token = request.META.get('HTTP_AUTHORIZATION').split()[1]
            # Blacklist the token
            token_obj = RefreshToken(token)
            token_obj.blacklist()
            return Response({"msg": "Successfully logged out."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"msg": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)
        
# inventory/views.py
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import InventoryItem
from .serializers import InventoryItemSerializer
import redis
import logging
from django.core.cache import cache

logger = logging.getLogger('inventory')

class ItemListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        items = InventoryItem.objects.all()
        serializer = InventoryItemSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = InventoryItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ItemDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, item_id):
        logger.info(f"Received request to get item with id: {item_id}")

        # Try to get the item from the cache first
        cached_item = cache.get(f"item_{item_id}")
        if cached_item:
            logger.info(f"Item {item_id} retrieved from cache.")
            return Response(cached_item)  # Return cached item if found

        # If the item is not in the cache, fetch it from the database
        try:
            item = InventoryItem.objects.get(id=item_id)
        except InventoryItem.DoesNotExist:
            logger.error(f"Item {item_id} not found.")
            return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)

        # Serialize the item
        serializer = InventoryItemSerializer(item)
        item_data = serializer.data

        # Cache the item data for future requests
        cache.set(f"item_{item_id}", item_data, timeout=300)  # Cache for 5 minutes (300 seconds)
        logger.info(f"Item {item_id} retrieved from database and cached.")
        return Response(item_data)


    def put(self, request, item_id):
        logger.info(f"Received request to update item with id: {item_id}")
        try:
            item = InventoryItem.objects.get(id=item_id)
        except InventoryItem.DoesNotExist:
            logger.error(f"Item {item_id} not found for update.")
            return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = InventoryItemSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
             # Clear the cache for this item after deleting it
            cache.delete(f"item_{item_id}")
            logger.info(f"Item {item_id} updated successfully.")
            return Response(serializer.data)
        logger.warning(f"Failed to update item {item_id}. Errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, item_id):
        logger.info(f"Received request to delete item with id: {item_id}")
        try:
            item = InventoryItem.objects.get(id=item_id)
        except InventoryItem.DoesNotExist:
            logger.error(f"Item {item_id} not found for deletion.")
            return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)
        
        item.delete()
         # Clear the cache for this item after deleting it
        cache.delete(f"item_{item_id}")
        logger.info(f"Item {item_id} deleted successfully.")
        return Response(status=status.HTTP_204_NO_CONTENT)
