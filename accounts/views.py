from django.shortcuts import render
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.contrib.auth.decorators import login_required
import json
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import CustomUserSerializer
from django.views.decorators.csrf import ensure_csrf_cookie


# Create your views here.


User = get_user_model()

@csrf_exempt
def signup_view(request):
    if request.method == 'POST':
        try:
            body = request.body.decode('utf-8')
            data = json.loads(body)
            email = data.get('email')
            password = data.get('password')

            if not email or not password:
                return JsonResponse({'error': 'Email and password are required'}, status=400)

            user = User.objects.create_user(
                username=email,
                email=email,
                password=password
            )

            login(request, user)

            return JsonResponse({
                'message': 'User created successfully',
                'email': user.email,
                'internal_id': str(user.internal_id)  # ★ 追加！
            }, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Only POST method allowed'}, status=405)


@ensure_csrf_cookie
def get_csrf_token(request):
    print("✅ get_csrf_token called — CSRF cookie should be set if not present.")
    return JsonResponse({'message': 'CSRF cookie set'})



@csrf_protect
@api_view(['POST'])
@permission_classes([])
def login_view(request):
    try:
        data = request.data  # JSONパース済み
        email = data.get('email')
        password = data.get('password')

        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({
                'message': 'Login successful',
                'email': user.email,
                'internal_id': str(user.internal_id)  
            }, status=200)
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=401)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    

@csrf_exempt
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return JsonResponse({'message': 'Logged out'}, status=200)
    return JsonResponse({'error': 'POST only'}, status=405)


@ensure_csrf_cookie
@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def me_view(request):
    user = request.user

    if request.method == 'GET':
        serializer = CustomUserSerializer(user)
        return Response(serializer.data)

    elif request.method == 'PATCH':
        serializer = CustomUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)