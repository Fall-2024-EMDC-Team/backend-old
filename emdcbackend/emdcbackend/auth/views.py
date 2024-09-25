from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404


@api_view(["GET"])
def user_by_id(request, user_id):  # Consistent parameter name
    user = get_object_or_404(User, id=user_id)  # Use user_id here
    serializer = UserSerializer(instance=user)
    return Response({"user": serializer.data}, status=status.HTTP_200_OK)


# login endpoint
@api_view(["POST"])
def login(request):
    user = get_object_or_404(
        User, username=request.data["username"]
    )  # check if user's email exists
    if not user.check_password(request.data["password"]):  # if password is incorrect
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
    token, created = Token.objects.get_or_create(user=user)
    serializer = UserSerializer(instance=user)
    return Response({"token": token.key, "user": serializer.data})


# signup endpoint
@api_view(["POST"])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()  # add user to DB
        user = User.objects.get(username=request.data["username"])
        user.set_password(request.data["password"])
        user.save()
        token = Token.objects.create(user=user)
        return Response({"token": token.key, "user": serializer.data})
    return Response(
        serializer.errors, status=status.HTTP_400_BAD_REQUEST
    )  # If data is bad


# delete user by id
@api_view(["DELETE"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def delete_user_by_id(request, user_id):
    user_to_delete = get_object_or_404(User, id=user_id)
    user_to_delete.delete()
    return Response({"detail": "User deleted successfully."}, status=status.HTTP_200_OK)


# edit user (password change, email change) API
@api_view(["POST"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def edit_user(request):
    user = get_object_or_404(User, id=request.data["id"])

    try:
        if User.objects.filter(username=request.data["username"]).exists():
            return Response(
                {"detail": "Username already taken."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.username = request.data["username"]
    except:
        pass

    try:
        user.set_password(request.data["password"])
    except:
        pass

    user.save()
    serializer = UserSerializer(instance=user)

    return Response({"user": serializer.data})


# token verification endpoint
@api_view(["GET"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def test_token(request):
    return Response({"passed for {}".format(request.user.username)})
