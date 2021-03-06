from app.models import *
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from rest_framework import serializers

class AuthenticationSerializer(serializers.ModelSerializer):
    access_token = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
    google_id = serializers.CharField()
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'access_token', 'google_id')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'last_login', 'date_joined')

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class TokenSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    class Meta:
        model = Token
        fields = ('key', 'user')
        read_only_fields = ('user',)

    def get_user(self, token):
        user = token.user
        serializer = UserSerializer(instance=user)
        return serializer.data

class PictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Picture
        fields = ('id', 'name', 'path', 'owner', 'uploaded', 'score', 'winner')

class VoteSerializer(serializers.ModelSerializer):
    token = serializers.CharField(write_only=True)
    class Meta:
        model = Vote
        fields = ('picture', 'value', 'token')

    def create(self, validated_data):
        value = validated_data['value']
        vote = Vote.objects.create(picture=validated_data['picture'], user=validated_data['user'], value=value)
        self.update_picture_score(vote.picture, value)
        return vote

    def update_picture_score(self, picture, value):
        picture = Picture.objects.get(pk=picture.pk)
        picture.score += value
        picture.save()
        return

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('picture', 'contact', 'user', 'time')
