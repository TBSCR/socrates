from app.models import *
from app.serializers import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.http import Http404
from django.contrib.sessions.backends.db import SessionStore
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.parsers import JSONParser, FileUploadParser
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status
import requests

session_store = SessionStore()

class Authenticate(APIView):
    """
    Get authentication token, or
    register user (if not registered already) and return user information.
    """
    parser_classes = (JSONParser,)
    def get(self, request, format=None):
        key = session_store.get('token', False)
        if not key:
            return Response({"message": "Credentials not given"})
        token = Token.objects.get(key=key)
        serializer = TokenSerializer(token)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = AuthenticationSerializer(data=request.data)
        if serializer.is_valid():
            token = request.data.get("access_token")
            # validate given token from google
            uri = "https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=" + token
            response = requests.get(uri)
            if (response.json().get("email") == request.data.get("email") and response.json().get("user_id") == request.data.get("google_id")):
                username = response.json().get("user_id")
                user, created = User.objects.get_or_create(username=username)
                if created:
                    user.first_name = request.data.get("first_name")
                    user.last_name = request.data.get("last_name")
                    user.email = request.data.get("email")
                    password = User.objects.make_random_password()
                    user.set_password(password)
                    user.save()
            token = Token.objects.get(user=user)
            response_data = {
                "token": token.key,
                "firstName": user.first_name,
                "lastName": user.last_name,
                "email": user.email
            }
            # store token key to session table
            session_store['token'] = token.key
            session_store.save()
            return Response(response_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Users(APIView):
    """
    List all users.
    """
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated, IsAdminUser,)
    parser_classes = (JSONParser,) # Content-Type: application/json
    def get(self, request, format=None):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

class Pictures(APIView):
    """
    List all pictures or create a new picture.
    """
    parser_classes = (JSONParser, FileUploadParser) # Content-Type: application/json
    def get(self, request, format=None):
        page = request.GET.get('page') if (request.GET.get('page') != None) else 1
        picture_list = Picture.objects.all()
        paginator = Paginator(picture_list, 5)

        try:
            pictures = paginator.page(page)
        except PageNotAnInteger:
            pictures = paginator.page(1)
        except EmptyPage:
            pictures = paginator.page(paginator.num_pages)

        serializer = PictureSerializer(pictures, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = PictureSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


"""  /pictures/winner  """
class Winner(APIView):
    """
    Get the latest winner picture.
    """
    parser_classes = (JSONParser, ) # Content-Type: application/json
    def get(self, request, format=None):
        winner = Picture.objects.filter(winner=True).order_by("uploaded").first()
        serializer = PictureSerializer(winner, many=False)
        return Response(serializer.data)

class Votes(APIView):
    """
    List all votes or create a new vote.
    """
    parser_classes = (JSONParser, ) # Content-Type: application/json
    def get(self, request, format=None):
        votes = Vote.objects.all()
        serializer = VoteSerializer(votes, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = VoteSerializer(data=request.data)
        if serializer.is_valid():
            token = request.data.get("token")
            user = Token.objects.get(key=token).user
            serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Orders(APIView):
    """
    List all orders or create a new order.
    """
    parser_classes = (JSONParser, ) # Content-Type: application/json
    def get(self, request, format=None):
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
