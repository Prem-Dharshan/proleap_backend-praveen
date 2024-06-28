from datetime import datetime, timedelta
from django.conf import settings
import jwt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .permissions import IsAuthenticatedVerifiedActive, IsAdmin, IsOrganizer, IsRegularUser, IsAdminOrOrganizer, IsAdminOrOrganizerOrUser
from django.shortcuts import get_object_or_404, redirect
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework_simplejwt.tokens import AccessToken, TokenError
from django.http import JsonResponse
import csv
import io
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from .swagger_schemas import activity_answer_response_schema
from .swagger_schemas import batch_activity_response_schema
from django.contrib.auth.hashers import make_password



from .models import User, Batch, UserBatch, Activity, UserActivity, Card, UserCard, Question, Option, Answer
from .serializers import (
    UserSerializer, BatchSerializer, UserBatchSerializer,
    ActivitySerializer, UserActivitySerializer,
    CardSerializer, UserCardSerializer,
    QuestionSerializer, OptionSerializer, AnswerSerializer
)


class UserListAPIView(APIView):

    permission_classes = [IsAuthenticatedVerifiedActive, IsAdminOrOrganizer]

    @swagger_auto_schema(
        operation_description="Retrieve a list of users",
        responses={200: UserSerializer(many=True)},
        manual_parameters=[
        openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                description="Bearer token",
                type=openapi.TYPE_STRING,
                required=True,
                examples={
                    'Bearer Token': {
                        'value': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzE5MzQ1MzYzLCJpYXQiOjE3MTkzNDE3NjMsImp0aSI6IjRkNTc0NjY3ZjQyZjQxZDE5NzcyOWNiMzg5MTIyYjU2IiwidXNlcl9pZCI6M30.ygESn-3hdcd-3x1HH0z9Rdpx2J3WZpce8PI3OZlRfRQ'
                    }
                }
            )
        ],
    )
    def get(self, request):
        try:
            users = User.objects.all()
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Create a new user",
        request_body=UserSerializer,
        responses={201: UserSerializer, 400: 'Bad Request'},
        manual_parameters=[
        openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                description="Bearer token",
                type=openapi.TYPE_STRING,
                required=True,
                examples={
                    'Bearer Token': {
                        'value': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzE5MzQ1MzYzLCJpYXQiOjE3MTkzNDE3NjMsImp0aSI6IjRkNTc0NjY3ZjQyZjQxZDE5NzcyOWNiMzg5MTIyYjU2IiwidXNlcl9pZCI6M30.ygESn-3hdcd-3x1HH0z9Rdpx2J3WZpce8PI3OZlRfRQ'
                    }
                }
            )
        ],
    )
    def post(self, request, format=None):
        try:
            serializer = UserSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            if serializer.is_valid():
                user = serializer.save()
                refresh = RefreshToken.for_user(user)
                user.set_password(serializer.validated_data['password'])
                user.save()
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': serializer.data
                }, status=status.HTTP_201_CREATED)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response({'error': str(e)},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserDetailAPIView(APIView):
    
    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAuthenticatedVerifiedActive, IsAdmin]
        return [IsAuthenticatedVerifiedActive(), IsAdminOrOrganizerOrUser()]
    

    @swagger_auto_schema(
        operation_description="Retrieve a user by ID",
        responses={200: UserSerializer, 404: 'Not Found'},
        manual_parameters=[
        openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                description="Bearer token",
                type=openapi.TYPE_STRING,
                required=True,
                examples={
                    'Bearer Token': {
                        'value': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzE5MzQ1MzYzLCJpYXQiOjE3MTkzNDE3NjMsImp0aSI6IjRkNTc0NjY3ZjQyZjQxZDE5NzcyOWNiMzg5MTIyYjU2IiwidXNlcl9pZCI6M30.ygESn-3hdcd-3x1HH0z9Rdpx2J3WZpce8PI3OZlRfRQ'
                    }
                }
            )
        ]
    )
    def get(self, request, id):
        try:
            user = User.objects.get(pk=id)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except TokenError as e:
            return Response({'error': 'Invalid token'},
                            status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({'error': 'User not found'},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Update a user by ID",
        request_body=UserSerializer,
        responses={200: UserSerializer, 400: 'Bad Request', 404: 'Not Found'},
        manual_parameters=[
        openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                description="Bearer token",
                type=openapi.TYPE_STRING,
                required=True,
                examples={
                    'Bearer Token': {
                        'value': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzE5MzQ1MzYzLCJpYXQiOjE3MTkzNDE3NjMsImp0aSI6IjRkNTc0NjY3ZjQyZjQxZDE5NzcyOWNiMzg5MTIyYjU2IiwidXNlcl9pZCI6M30.ygESn-3hdcd-3x1HH0z9Rdpx2J3WZpce8PI3OZlRfRQ'
                    }
                }
            )
        ],
    )
    def put(self, request, id):
        try:
            user = User.objects.get(pk=id)
            serializer = UserSerializer(user, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response({'error': str(e)},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Delete a user by ID",
        responses={204: 'No Content', 404: 'Not Found'},
        manual_parameters=[
        openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                description="Bearer token",
                type=openapi.TYPE_STRING,
                required=True,
                examples={
                    'Bearer Token': {
                        'value': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzE5MzQ1MzYzLCJpYXQiOjE3MTkzNDE3NjMsImp0aSI6IjRkNTc0NjY3ZjQyZjQxZDE5NzcyOWNiMzg5MTIyYjU2IiwidXNlcl9pZCI6M30.ygESn-3hdcd-3x1HH0z9Rdpx2J3WZpce8PI3OZlRfRQ'
                    }
                }
            )
        ],
    )
    def delete(self, request, id):
        try:
            user = User.objects.get(pk=id)
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SignInAPIView(APIView):

    permission_classes = [AllowAny]     # TODO: Atleast provide basic security

    @swagger_auto_schema(
        tags=[
            'auth',
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=[
                'email',
                'password'],
            properties={
                'email': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='User email'),
                'password': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='User password'),
            }),
        responses={
            200: openapi.Response(
                description='Successful login',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'refresh': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='Refresh token'),
                        'access': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='Access token'),
                        'user_id': openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description='User ID'),
                    })),
            400: 'Invalid input',
            401: 'Unauthorized'},
        #     manual_parameters=[
        # openapi.Parameter(
        #         name='Authorization',
        #         in_=openapi.IN_HEADER,
        #         description="Bearer token",
        #         type=openapi.TYPE_STRING,
        #         required=True,
        #         examples={
        #             'Bearer Token': {
        #                 'value': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzE5MzQ1MzYzLCJpYXQiOjE3MTkzNDE3NjMsImp0aSI6IjRkNTc0NjY3ZjQyZjQxZDE5NzcyOWNiMzg5MTIyYjU2IiwidXNlcl9pZCI6M30.ygESn-3hdcd-3x1HH0z9Rdpx2J3WZpce8PI3OZlRfRQ'
        #             }
        #         }
        #     )
        # ],
        )
    def post(self, request, format=None):
        email = request.data.get('email')
        password = request.data.get('password')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User not found'},
                            status=status.HTTP_404_NOT_FOUND)

        try:
            latest_user_batch = UserBatch.objects.filter(
                user=user).order_by('updated_at').first()
            batch_id = latest_user_batch.batch.id
            batch_name = latest_user_batch.batch.name
        except UserBatch.DoesNotExist:
            return JsonResponse({'error': 'UserBatch not found'}, status=404)

        if (user.check_password(password)):
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user_id': user.id,
                'username': user.username,
                'batch_id': batch_id,
                'batch_name': batch_name
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'},
                            status=status.HTTP_401_UNAUTHORIZED)


class BatchListCreateAPIView(APIView):

    permission_classes = [IsAuthenticatedVerifiedActive, IsAdminOrOrganizer]

    @swagger_auto_schema(operation_description="List all batches",
                         responses={200: BatchSerializer(many=True),
                                    500: openapi.Response(description='Internal Server Error')},
                        manual_parameters=[
        openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                description="Bearer token",
                type=openapi.TYPE_STRING,
                required=True,
                examples={
                    'Bearer Token': {
                        'value': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzE5MzQ1MzYzLCJpYXQiOjE3MTkzNDE3NjMsImp0aSI6IjRkNTc0NjY3ZjQyZjQxZDE5NzcyOWNiMzg5MTIyYjU2IiwidXNlcl9pZCI6M30.ygESn-3hdcd-3x1HH0z9Rdpx2J3WZpce8PI3OZlRfRQ'
                    }
                }
            )
        ],)
    def get(self, request):
        try:
            batches = Batch.objects.all()
            serializer = BatchSerializer(batches, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Create a new batch",
        request_body=BatchSerializer,
        responses={
            201: BatchSerializer,
            400: openapi.Response(description='Invalid input'),
            500: openapi.Response(description='Internal Server Error')
        },
        manual_parameters=[
        openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                description="Bearer token",
                type=openapi.TYPE_STRING,
                required=True,
                examples={
                    'Bearer Token': {
                        'value': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzE5MzQ1MzYzLCJpYXQiOjE3MTkzNDE3NjMsImp0aSI6IjRkNTc0NjY3ZjQyZjQxZDE5NzcyOWNiMzg5MTIyYjU2IiwidXNlcl9pZCI6M30.ygESn-3hdcd-3x1HH0z9Rdpx2J3WZpce8PI3OZlRfRQ'
                    }
                }
            )
        ],
    )
    def post(self, request):
        try:
            serializer = BatchSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BatchDetailAPIView(APIView):

    permission_classes = [IsAuthenticatedVerifiedActive, IsAdminOrOrganizer]


    @swagger_auto_schema(
        operation_description="Retrieve a batch by ID",
        responses={
            200: BatchSerializer,
            404: openapi.Response(description='Not Found'),
            500: openapi.Response(description='Internal Server Error')
        },
        manual_parameters=[
        openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                description="Bearer token",
                type=openapi.TYPE_STRING,
                required=True,
                examples={
                    'Bearer Token': {
                        'value': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzE5MzQ1MzYzLCJpYXQiOjE3MTkzNDE3NjMsImp0aSI6IjRkNTc0NjY3ZjQyZjQxZDE5NzcyOWNiMzg5MTIyYjU2IiwidXNlcl9pZCI6M30.ygESn-3hdcd-3x1HH0z9Rdpx2J3WZpce8PI3OZlRfRQ'
                    }
                }
            )
        ],
    )
    def get(self, request, pk):
        try:
            batch = Batch.objects.get(pk=pk)
            serializer = BatchSerializer(batch)
            return Response(serializer.data)
        except Batch.DoesNotExist:
            return Response({'error': 'Batch not found'},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Update a batch by ID",
        request_body=BatchSerializer,
        responses={
            200: BatchSerializer,
            400: openapi.Response(description='Invalid input'),
            404: openapi.Response(description='Not Found'),
            500: openapi.Response(description='Internal Server Error')
        },
        manual_parameters=[
        openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                description="Bearer token",
                type=openapi.TYPE_STRING,
                required=True,
                examples={
                    'Bearer Token': {
                        'value': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzE5MzQ1MzYzLCJpYXQiOjE3MTkzNDE3NjMsImp0aSI6IjRkNTc0NjY3ZjQyZjQxZDE5NzcyOWNiMzg5MTIyYjU2IiwidXNlcl9pZCI6M30.ygESn-3hdcd-3x1HH0z9Rdpx2J3WZpce8PI3OZlRfRQ'
                    }
                }
            )
        ],
    )
    def put(self, request, pk):
        try:
            batch = Batch.objects.get(pk=pk)
            serializer = BatchSerializer(batch, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)
        except Batch.DoesNotExist:
            return Response({'error': 'Batch not found'},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Delete a batch by ID",
        responses={
            204: openapi.Response(description='No Content'),
            404: openapi.Response(description='Not Found'),
            500: openapi.Response(description='Internal Server Error')
        },
        manual_parameters=[
        openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                description="Bearer token",
                type=openapi.TYPE_STRING,
                required=True,
                examples={
                    'Bearer Token': {
                        'value': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzE5MzQ1MzYzLCJpYXQiOjE3MTkzNDE3NjMsImp0aSI6IjRkNTc0NjY3ZjQyZjQxZDE5NzcyOWNiMzg5MTIyYjU2IiwidXNlcl9pZCI6M30.ygESn-3hdcd-3x1HH0z9Rdpx2J3WZpce8PI3OZlRfRQ'
                    }
                }
            )
        ],
    )
    def delete(self, request, pk):
        try:
            batch = Batch.objects.get(pk=pk)
            batch.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Batch.DoesNotExist:
            return Response({'error': 'Batch not found'},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserBatchListCreateAPIView(APIView):

    permission_classes = [IsAuthenticatedVerifiedActive, IsAdminOrOrganizer]

    @swagger_auto_schema(
        operation_description="List all user batches", responses={
            200: UserBatchSerializer(
                many=True), 500: openapi.Response(
                description='Internal Server Error')},
                manual_parameters=[
        openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                description="Bearer token",
                type=openapi.TYPE_STRING,
                required=True,
                examples={
                    'Bearer Token': {
                        'value': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzE5MzQ1MzYzLCJpYXQiOjE3MTkzNDE3NjMsImp0aSI6IjRkNTc0NjY3ZjQyZjQxZDE5NzcyOWNiMzg5MTIyYjU2IiwidXNlcl9pZCI6M30.ygESn-3hdcd-3x1HH0z9Rdpx2J3WZpce8PI3OZlRfRQ'
                    }
                }
            )
        ],)
    def get(self, request):
        try:
            user_batches = UserBatch.objects.all()
            serializer = UserBatchSerializer(user_batches, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Create a new user batch",
        request_body=UserBatchSerializer,
        responses={201: UserBatchSerializer, 400: 'Invalid input'},
        manual_parameters=[
        openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                description="Bearer token",
                type=openapi.TYPE_STRING,
                required=True,
                examples={
                    'Bearer Token': {
                        'value': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzE5MzQ1MzYzLCJpYXQiOjE3MTkzNDE3NjMsImp0aSI6IjRkNTc0NjY3ZjQyZjQxZDE5NzcyOWNiMzg5MTIyYjU2IiwidXNlcl9pZCI6M30.ygESn-3hdcd-3x1HH0z9Rdpx2J3WZpce8PI3OZlRfRQ'
                    }
                }
            )
        ],
    )
    def post(self, request):
        try:
            serializer = UserBatchSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserBatchDetailAPIView(APIView):

    permission_classes = [IsAuthenticatedVerifiedActive, IsAdminOrOrganizer]


    @swagger_auto_schema(
        operation_description="Retrieve a user batch by ID",
        responses={
            200: UserBatchSerializer,
            404: openapi.Response(description='Not Found'),
            500: openapi.Response(description='Internal Server Error')
        },
        manual_parameters=[
        openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                description="Bearer token",
                type=openapi.TYPE_STRING,
                required=True,
                examples={
                    'Bearer Token': {
                        'value': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzE5MzQ1MzYzLCJpYXQiOjE3MTkzNDE3NjMsImp0aSI6IjRkNTc0NjY3ZjQyZjQxZDE5NzcyOWNiMzg5MTIyYjU2IiwidXNlcl9pZCI6M30.ygESn-3hdcd-3x1HH0z9Rdpx2J3WZpce8PI3OZlRfRQ'
                    }
                }
            )
        ],
    )
    def get(self, request, pk):
        try:
            user_batch = UserBatch.objects.get(pk=pk)
            serializer = UserBatchSerializer(user_batch)
            return Response(serializer.data)
        except UserBatch.DoesNotExist:
            return Response({'error': 'UserBatch not found'},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Update a user batch by ID",
        request_body=UserBatchSerializer,
        responses={
            200: UserBatchSerializer,
            400: openapi.Response(description='Invalid input'),
            404: openapi.Response(description='Not Found'),
            500: openapi.Response(description='Internal Server Error')
        },
        manual_parameters=[
        openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                description="Bearer token",
                type=openapi.TYPE_STRING,
                required=True,
                examples={
                    'Bearer Token': {
                        'value': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzE5MzQ1MzYzLCJpYXQiOjE3MTkzNDE3NjMsImp0aSI6IjRkNTc0NjY3ZjQyZjQxZDE5NzcyOWNiMzg5MTIyYjU2IiwidXNlcl9pZCI6M30.ygESn-3hdcd-3x1HH0z9Rdpx2J3WZpce8PI3OZlRfRQ'
                    }
                }
            )
        ],
    )
    def put(self, request, pk):
        try:
            user_batch = UserBatch.objects.get(pk=pk)
            serializer = UserBatchSerializer(user_batch, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)
        except UserBatch.DoesNotExist:
            return Response({'error': 'UserBatch not found'},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Delete a user batch by ID",
        responses={
            204: openapi.Response(description='No Content'),
            404: openapi.Response(description='Not Found'),
            500: openapi.Response(description='Internal Server Error')
        },
        manual_parameters=[
        openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                description="Bearer token",
                type=openapi.TYPE_STRING,
                required=True,
                examples={
                    'Bearer Token': {
                        'value': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzE5MzQ1MzYzLCJpYXQiOjE3MTkzNDE3NjMsImp0aSI6IjRkNTc0NjY3ZjQyZjQxZDE5NzcyOWNiMzg5MTIyYjU2IiwidXNlcl9pZCI6M30.ygESn-3hdcd-3x1HH0z9Rdpx2J3WZpce8PI3OZlRfRQ'
                    }
                }
            )
        ],
    )
    def delete(self, request, pk):
        try:
            user_batch = UserBatch.objects.get(pk=pk)
            user_batch.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except UserBatch.DoesNotExist:
            return Response({'error': 'UserBatch not found'},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BatchUserListAPIView(APIView):

    permission_classes = [IsAuthenticatedVerifiedActive, IsAdminOrOrganizer]


    @swagger_auto_schema(tags=['batches'],
                         operation_description="List all users of a batch",
                         responses={200: UserBatchSerializer(many=True),
                                    500: openapi.Response(description='Internal Server Error')})
    def get_users(self, request, batch_id):
        try:
            user_batches = UserBatch.objects.filter(batch_id=batch_id)
            serializer = UserBatchSerializer(user_batches, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(tags=['users'],
                         operation_description="List all batches of a user",
                         responses={200: UserBatchSerializer(many=True),
                                    500: openapi.Response(description='Internal Server Error')})
    def get_batches(self, request, user_id):
        try:
            user_batches = UserBatch.objects.filter(user_id=user_id)
            serializer = UserBatchSerializer(user_batches, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        tags=['batches-users-list',],
        manual_parameters=[
            openapi.Parameter('batch_id', openapi.IN_QUERY,
                              description="ID of the batch", type=openapi.TYPE_INTEGER),
            openapi.Parameter('user_id', openapi.IN_QUERY,
                              description="ID of the user", type=openapi.TYPE_INTEGER)
        ],
        responses={
            200: UserBatchSerializer(many=True),
            400: openapi.Response(description='Bad Request'),
            500: openapi.Response(description='Internal Server Error')
        },
        operation_description="List users of a batch or batches of a user based on the provided query parameter"
    )
    def get(self, request, *args, **kwargs):
        batch_id = request.query_params.get('batch_id')
        user_id = request.query_params.get('user_id')

        if batch_id and user_id:
            return Response(
                {
                    'error': 'Only one of batch_id or user_id should be provided'},
                status=status.HTTP_400_BAD_REQUEST)
        elif not batch_id and not user_id:
            return Response({'error': 'Either batch_id or user_id must be provided'},
                            status=status.HTTP_400_BAD_REQUEST)
        elif batch_id:
            return self.get_users(request, batch_id)
        elif user_id:
            return self.get_batches(request, user_id)


class ActivityListCreateAPIView(APIView):

    permission_classes = [IsAuthenticatedVerifiedActive, IsAdminOrOrganizer]

    @swagger_auto_schema(operation_description="List all activities",
                         responses={200: ActivitySerializer(many=True),
                                    500: openapi.Response(description='Internal Server Error')})
    def get(self, request):
        try:
            activities = Activity.objects.all()
            serializer = ActivitySerializer(activities, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Create a new activity",
        request_body=ActivitySerializer,
        responses={
            201: ActivitySerializer,
            400: openapi.Response(description='Invalid input'),
            500: openapi.Response(description='Internal Server Error')
        }
    )
    def post(self, request):
        try:
            serializer = ActivitySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ActivityDetailAPIView(APIView):

    permission_classes = [IsAuthenticatedVerifiedActive, IsAdminOrOrganizer]

    @swagger_auto_schema(
        operation_description="Retrieve a activity by ID",
        responses={
            200: ActivitySerializer,
            404: openapi.Response(description='Not Found'),
            500: openapi.Response(description='Internal Server Error')
        }
    )
    def get(self, request, pk):
        try:
            activity = Activity.objects.get(pk=pk)
            serializer = ActivitySerializer(activity)
            return Response(serializer.data)
        except Activity.DoesNotExist:
            return Response({'error': 'Activity not found'},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Update an activity by ID",
        request_body=ActivitySerializer,
        responses={
            200: ActivitySerializer,
            400: openapi.Response(description='Invalid input'),
            404: openapi.Response(description='Not Found'),
            500: openapi.Response(description='Internal Server Error')
        }
    )
    def put(self, request, pk):  # TODO: Upon update, shouldn't be able to change Batch FK
        try:
            activity = Activity.objects.get(pk=pk)
            serializer = ActivitySerializer(activity, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)
        except Activity.DoesNotExist:
            return Response({'error': 'Activity not found'},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Delete an activity by ID",
        responses={
            204: openapi.Response(description='No Content'),
            404: openapi.Response(description='Not Found'),
            500: openapi.Response(description='Internal Server Error')
        }
    )
    def delete(self, request, pk):
        try:
            activity = Activity.objects.get(pk=pk)
            activity.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Activity.DoesNotExist:
            return Response({'error': 'Activity not found'},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserActivityListCreateAPIView(APIView):
    
    permission_classes = [IsAuthenticatedVerifiedActive, IsAdminOrOrganizer]

    @swagger_auto_schema(
        operation_description="List all user activities", responses={
            200: UserActivitySerializer(
                many=True), 500: openapi.Response(
                description='Internal Server Error')})
    def get(self, request):
        try:
            user_activities = UserActivity.objects.all()
            serializer = UserActivitySerializer(user_activities, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Create a new user activity",
        request_body=UserActivitySerializer,
        responses={
            201: UserActivitySerializer,
            400: openapi.Response(description='Invalid input'),
            500: openapi.Response(description='Internal Server Error')
        }
    )
    def post(self, request):
        try:
            serializer = UserActivitySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserActivityDetailAPIView(APIView):

    permission_classes = [IsAuthenticatedVerifiedActive, IsAdminOrOrganizer]

    @swagger_auto_schema(
        operation_description="Retrieve a user activity by ID",
        responses={
            200: UserActivitySerializer,
            404: openapi.Response(description='Not Found'),
            500: openapi.Response(description='Internal Server Error')
        }
    )
    def get(self, request, pk):
        try:
            user_activity = UserActivity.objects.get(pk=pk)
            serializer = UserActivitySerializer(user_activity)
            return Response(serializer.data)
        except UserActivity.DoesNotExist:
            return Response({'error': 'UserActivity not found'},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Update a user activity by ID",
        request_body=UserActivitySerializer,
        responses={
            200: UserActivitySerializer,
            400: openapi.Response(description='Invalid input'),
            404: openapi.Response(description='Not Found'),
            500: openapi.Response(description='Internal Server Error')
        }
    )
    def put(self, request, pk):
        try:
            user_activity = UserActivity.objects.get(pk=pk)
            serializer = UserActivitySerializer(
                user_activity, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)
        except UserActivity.DoesNotExist:
            return Response({'error': 'UserActivity not found'},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Delete a user activity by ID",
        responses={
            204: openapi.Response(description='No Content'),
            404: openapi.Response(description='Not Found'),
            500: openapi.Response(description='Internal Server Error')
        }
    )
    def delete(self, request, pk):
        try:
            user_activity = UserActivity.objects.get(pk=pk)
            user_activity.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except UserActivity.DoesNotExist:
            return Response({'error': 'UserActivity not found'},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CardListCreateAPIView(APIView):

    permission_classes = [IsAuthenticatedVerifiedActive, IsAdminOrOrganizer]

    @swagger_auto_schema(operation_description="List all cards",
                         responses={200: CardSerializer(many=True),
                                    500: openapi.Response(description='Internal Server Error')})
    def get(self, request):
        try:
            cards = Card.objects.all()
            serializer = CardSerializer(cards, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Create a new card",
        request_body=CardSerializer,
        responses={
            201: CardSerializer,
            400: openapi.Response(description='Invalid input'),
            500: openapi.Response(description='Internal Server Error')
        }
    )
    def post(self, request):
        try:
            serializer = CardSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CardDetailAPIView(APIView):

    permission_classes = [IsAuthenticatedVerifiedActive, IsAdminOrOrganizer]

    @swagger_auto_schema(
        operation_description="Retrieve a card by ID",
        responses={
            200: CardSerializer,
            404: openapi.Response(description='Not Found'),
            500: openapi.Response(description='Internal Server Error')
        }
    )
    def get(self, request, pk):
        try:
            card = Card.objects.get(pk=pk)
            serializer = CardSerializer(card)
            return Response(serializer.data)
        except Card.DoesNotExist:
            return Response({'error': 'Card not found'},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Update an card by ID",
        request_body=CardSerializer,
        responses={
            200: CardSerializer,
            400: openapi.Response(description='Invalid input'),
            404: openapi.Response(description='Not Found'),
            500: openapi.Response(description='Internal Server Error')
        }
    )
    def put(self, request, pk):  # TODO: Upon update, shouldn't be able to change Batch FK
        try:
            card = Card.objects.get(pk=pk)
            serializer = CardSerializer(card, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)
        except Card.DoesNotExist:
            return Response({'error': 'Card not found'},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Delete an card by ID",
        responses={
            204: openapi.Response(description='No Content'),
            404: openapi.Response(description='Not Found'),
            500: openapi.Response(description='Internal Server Error')
        }
    )
    def delete(self, request, pk):
        try:
            # TODO: Mark all delete views as inactive=true, add a field
            card = Card.objects.get(pk=pk)
            card.delete()  # TODO: Return the deleted object instead of None
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Card.DoesNotExist:
            return Response({'error': 'Card not found'},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserCardListCreateAPIView(APIView):

    permission_classes = [IsAuthenticatedVerifiedActive, IsAdminOrOrganizer]

    @swagger_auto_schema(operation_description="List all user card",
                         responses={200: UserCardSerializer(many=True),
                                    500: openapi.Response(description='Internal Server Error')})
    def get(self, request):
        try:
            user_cards = UserCard.objects.all()
            serializer = UserCardSerializer(user_cards, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Create a new user card",
        request_body=UserCardSerializer,
        responses={
            201: UserCardSerializer,
            400: openapi.Response(description='Invalid input'),
            500: openapi.Response(description='Internal Server Error')
        }
    )
    def post(self, request):
        try:
            serializer = UserCardSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserCardDetailAPIView(APIView):

    permission_classes = [IsAuthenticatedVerifiedActive, IsAdminOrOrganizer]

    @swagger_auto_schema(
        operation_description="Retrieve a user card by ID",
        responses={
            200: UserCardSerializer,
            404: openapi.Response(description='Not Found'),
            500: openapi.Response(description='Internal Server Error')
        }
    )
    def get(self, request, pk):
        try:
            user_card = UserCard.objects.get(pk=pk)
            serializer = UserCardSerializer(user_card)
            return Response(serializer.data)
        except UserCard.DoesNotExist:
            return Response({'error': 'UserCard not found'},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Update a user card by ID",
        request_body=UserCardSerializer,
        responses={
            200: UserCardSerializer,
            400: openapi.Response(description='Invalid input'),
            404: openapi.Response(description='Not Found'),
            500: openapi.Response(description='Internal Server Error')
        }
    )
    def put(self, request, pk):
        try:
            user_card = UserCard.objects.get(pk=pk)
            serializer = UserCardSerializer(user_card, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)
        except UserCard.DoesNotExist:
            return Response({'error': 'UserCard not found'},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Delete a user card by ID",
        responses={
            204: openapi.Response(description='No Content'),
            404: openapi.Response(description='Not Found'),
            500: openapi.Response(description='Internal Server Error')
        }
    )
    def delete(self, request, pk):
        try:
            user_card = UserCard.objects.get(pk=pk)
            user_card.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except UserCard.DoesNotExist:
            return Response({'error': 'UserCard not found'},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QuestionListCreateAPIView(APIView):

    permission_classes = [IsAuthenticatedVerifiedActive, IsAdminOrOrganizer]

    @swagger_auto_schema(operation_description="List all questions",
                         responses={200: QuestionSerializer(many=True),
                                    500: openapi.Response(description='Internal Server Error')})
    def get(self, request):
        try:
            questions = Question.objects.all()
            serializer = QuestionSerializer(questions, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Create a new question",
        request_body=QuestionSerializer,
        responses={
            201: QuestionSerializer,
            400: openapi.Response(description='Invalid input'),
            500: openapi.Response(description='Internal Server Error')
        }
    )
    def post(self, request):
        try:
            serializer = QuestionSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QuestionDetailAPIView(APIView):

    permission_classes = [IsAuthenticatedVerifiedActive, IsAdminOrOrganizer]

    @swagger_auto_schema(
        operation_description="Retrieve a question by ID",
        responses={
            200: QuestionSerializer,
            404: openapi.Response(description='Not Found'),
            500: openapi.Response(description='Internal Server Error')
        }
    )
    def get(self, request, pk):
        try:
            question = Question.objects.get(pk=pk)
            serializer = QuestionSerializer(question)
            return Response(serializer.data)
        except Question.DoesNotExist:
            return Response({'error': 'Question not found'},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Update a question by ID",
        request_body=QuestionSerializer,
        responses={
            200: QuestionSerializer,
            400: openapi.Response(description='Invalid input'),
            404: openapi.Response(description='Not Found'),
            500: openapi.Response(description='Internal Server Error')
        }
    )
    def put(self, request, pk):
        try:
            question = Question.objects.get(pk=pk)
            serializer = QuestionSerializer(question, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)
        except Question.DoesNotExist:
            return Response({'error': 'Question not found'},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Delete a question by ID",
        responses={
            204: openapi.Response(description='No Content'),
            404: openapi.Response(description='Not Found'),
            500: openapi.Response(description='Internal Server Error')
        }
    )
    def delete(self, request, pk):
        try:
            question = Question.objects.get(pk=pk)
            question.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Question.DoesNotExist:
            return Response({'error': 'Question not found'},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OptionListCreateAPIView(APIView):

    permission_classes = [IsAuthenticatedVerifiedActive, IsAdminOrOrganizer]

    @swagger_auto_schema(operation_description="List all options",
                         responses={200: OptionSerializer(many=True),
                                    500: openapi.Response(description='Internal Server Error')})
    def get(self, request):
        try:
            options = Option.objects.all()
            serializer = OptionSerializer(options, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Create a new option",
        request_body=OptionSerializer,
        responses={
            201: OptionSerializer,
            400: openapi.Response(description='Invalid input'),
            500: openapi.Response(description='Internal Server Error')
        }
    )
    def post(self, request):
        try:
            serializer = OptionSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OptionDetailAPIView(APIView):

    permission_classes = [IsAuthenticatedVerifiedActive, IsAdminOrOrganizer]

    @swagger_auto_schema(
        operation_description="Retrieve an option by ID",
        responses={
            200: OptionSerializer,
            404: openapi.Response(description='Not Found'),
            500: openapi.Response(description='Internal Server Error')
        }
    )
    def get(self, request, pk):
        try:
            option = Option.objects.get(pk=pk)
            serializer = OptionSerializer(option)
            return Response(serializer.data)
        except Option.DoesNotExist:
            return Response({'error': 'Option not found'},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Update an option by ID",
        request_body=OptionSerializer,
        responses={
            200: OptionSerializer,
            400: openapi.Response(description='Invalid input'),
            404: openapi.Response(description='Not Found'),
            500: openapi.Response(description='Internal Server Error')
        }
    )
    def put(self, request, pk):
        try:
            option = Option.objects.get(pk=pk)
            serializer = OptionSerializer(option, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)
        except Option.DoesNotExist:
            return Response({'error': 'Option not found'},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Delete an option by ID",
        responses={
            204: openapi.Response(description='No Content'),
            404: openapi.Response(description='Not Found'),
            500: openapi.Response(description='Internal Server Error')
        }
    )
    def delete(self, request, pk):
        try:
            option = Option.objects.get(pk=pk)
            option.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Option.DoesNotExist:
            return Response({'error': 'Option not found'},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AnswerListCreateAPIView(APIView):
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticatedVerifiedActive(), IsAdminOrOrganizerOrUser()]
        return [IsAuthenticatedVerifiedActive(), IsAdminOrOrganizer()]
    

    @swagger_auto_schema(operation_description="List all answers",
                         responses={200: AnswerSerializer(many=True),
                                    500: openapi.Response(description='Internal Server Error')})
    def get(self, request):
        try:
            answers = Answer.objects.all()
            serializer = AnswerSerializer(answers, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Create a new answer",
        request_body=AnswerSerializer,
        responses={
            201: AnswerSerializer,
            400: openapi.Response(description='Invalid input'),
            500: openapi.Response(description='Internal Server Error')
        }
    )
    def post(self, request):
        try:
            serializer = AnswerSerializer(data=request.data)
            if serializer.is_valid():
                answer_instances = serializer.save()

                if not isinstance(answer_instances, list):
                    answer_instances = [answer_instances]

                return Response(
                    AnswerSerializer(answer_instances, many=True).data,
                    status=status.HTTP_201_CREATED)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AnswerDetailAPIView(APIView):
    
    permission_classes = [IsAuthenticatedVerifiedActive, IsAdminOrOrganizerOrUser]

    @swagger_auto_schema(
        operation_description="Retrieve an answer by ID",
        responses={
            200: AnswerSerializer,
            404: openapi.Response(description='Not Found'),
            500: openapi.Response(description='Internal Server Error')
        }
    )
    def get(self, request, pk):
        try:
            answer = Answer.objects.get(pk=pk)
            serializer = AnswerSerializer(answer)
            return Response(serializer.data)
        except Answer.DoesNotExist:
            return Response({'error': 'Answer not found'},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Update an answer by ID",
        request_body=AnswerSerializer,
        responses={
            200: AnswerSerializer,
            400: openapi.Response(description='Invalid input'),
            404: openapi.Response(description='Not Found'),
            500: openapi.Response(description='Internal Server Error')
        }
    )
    def put(self, request, pk):
        try:
            answer = Answer.objects.get(pk=pk)
            serializer = AnswerSerializer(answer, data=request.data)
            if serializer.is_valid():
                if 'password' in serializer.validated_data:
                    new_password = serializer.validated_data['password']
                    if not answer.check_password(new_password):
                        serializer.validated_data['password'] = make_password(new_password)
                serializer.save()
                return Response(serializer.data)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)
        except Answer.DoesNotExist:
            return Response({'error': 'Answer not found'},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    @swagger_auto_schema(
        operation_description="Delete an answer by ID",
        responses={
            204: openapi.Response(description='No Content'),
            404: openapi.Response(description='Not Found'),
            500: openapi.Response(description='Internal Server Error')
        }
    )
    def delete(self, request, pk):
        try:
            answer = Answer.objects.get(pk=pk)
            answer.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Answer.DoesNotExist:
            return Response({'error': 'Answer not found'},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserRegister(APIView):
    
    permission_classes = [IsAuthenticatedVerifiedActive, IsAdminOrOrganizer]


    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(
        operation_summary="Upload CSV to register users",
        operation_description="Endpoint to register users from a CSV file. Each row in the CSV should contain fields: email, username, name, role, gender, phoneNumber.",
        consumes=["multipart/form-data"],
        responses={
            201: openapi.Response(
                description='Users registered and emails sent',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='Message indicating successful registration and email sending')})),
            400: 'Invalid input',
            415: 'Unsupported Media Type',
        })
    def post(self, request):
        file = request.FILES.get('file')

        if not file:
            return Response({'error': 'No file uploaded'},
                            status=status.HTTP_400_BAD_REQUEST)

        if not file.name.endswith('.csv'):
            return Response({'error': 'This is not a CSV file'},
                            status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

        try:
            data = file.read().decode('utf-8')
            io_string = io.StringIO(data)
            csv_reader = csv.reader(io_string, delimiter=',')
            header = next(csv_reader)
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_400_BAD_REQUEST)

        success_count = 0
        errors = []

        for row in csv_reader:
            try:
                email, username, name, role, gender, phone_number = row

                # Process each row
                name = name or ''
                role = role or 'USER'
                gender = gender or ''
                phone_number = phone_number or None

                user = User.objects.create_user(
                    email=email,
                    username=username,
                    name=name,
                    role=role,
                    gender=gender,
                    password='proleap',
                    phoneNumber=phone_number,
                    is_verified=False
                )

                user.set_password('string')
                user.save()

                # Generate JWT token for verification
                token_payload = {
                    'user_id': user.id,
                    'email': user.email,
                    'exp': datetime.now() + timedelta(hours=24)  # Token valid for 24 hours
                }
                token = jwt.encode(
                    token_payload,
                    settings.SECRET_KEY,
                    algorithm='HS256')

                # Build verification URL
                current_site = get_current_site(request)
                domain = current_site.domain
                verification_url = f"http://{domain}/apis/verify/{token}/"

                # Send email with verification link
                subject = 'Activate your account'
                # message = render_to_string('verification_email.html', {
                #     'user': user,
                #     'verification_url': verification_url,
                # })
                message = f'Please click the following link to verify your account: {
                    verification_url}'

                email = EmailMessage(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                )
                email.send()

                success_count += 1
            except Exception as e:
                errors.append(f'Error processing row: {str(e)}')

        if errors:
            return Response({'errors': errors},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {
                    'success': f'{success_count} users have been registered and emails sent'},
                status=status.HTTP_201_CREATED)


class VerifyEmail(APIView):

    permission_classes = [AllowAny]


    def get(self, request, token):
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=['HS256'])
            user = get_object_or_404(User, id=payload['user_id'])
        except jwt.ExpiredSignatureError:
            return JsonResponse(
                {'error': 'Verification link has expired'}, status=400)
        except jwt.InvalidTokenError:
            return JsonResponse(
                {'error': 'Invalid verification link'}, status=400)
        except User.ObjectDoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)

        user.is_verified = True
        user.save(update_fields=['is_verified'])

        try:
            latest_user_batch = UserBatch.objects.filter(
                user=user).latest('updated_at')
            batch_id = latest_user_batch.id
            batch_name = latest_user_batch.batch.name
        except UserBatch.DoesNotExist:
            return JsonResponse({'error': 'UserBatch not found'}, status=404)

        # response_data = {
        #     'message': 'Email verification successful',
        #     'user_id': user.id,
        #     'username': user.username,
        #     'batch_id': batch_id,
        #     'batch_name': batch_name
        # }

        # return JsonResponse(response_data)
        return redirect('http://127.0.0.1:3000/')


class UserCardQuestionProgress(APIView):
    
    permission_classes = [IsAuthenticatedVerifiedActive, IsAdminOrOrganizerOrUser]


    @swagger_auto_schema(
        operation_description="Retrieve the latest card and user progress for a specific activity.",
        responses={
            200: activity_answer_response_schema,
            400: 'Bad Request',
            404: 'Not Found',
            500: 'Internal Server Error'},
        manual_parameters=[
        openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                description="Bearer token",
                type=openapi.TYPE_STRING,
                required=True,
                examples={
                    'Bearer Token': {
                        'value': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzE5MzQ1MzYzLCJpYXQiOjE3MTkzNDE3NjMsImp0aSI6IjRkNTc0NjY3ZjQyZjQxZDE5NzcyOWNiMzg5MTIyYjU2IiwidXNlcl9pZCI6M30.ygESn-3hdcd-3x1HH0z9Rdpx2J3WZpce8PI3OZlRfRQ'
                    }
                }
            )
        ],
        )
    def get(self, request, user_id, activity_id):
        try:
            latest_user_card = UserCard.objects.filter(
                user_id=user_id, card__activity_id=activity_id).order_by('-updated_at').first()
            first_user_card = Card.objects.filter(activity=activity_id).order_by('created_at').first()
            last_card_id = latest_user_card.card.id if latest_user_card else (
                first_user_card.id if first_user_card else None)

            if not last_card_id:
                return Response(
                    {'error': 'No UserCard found for the user'}, status=status.HTTP_404_NOT_FOUND)

            try:
                activity = Activity.objects.get(id=activity_id)
            except Activity.DoesNotExist:
                return Response({'error': 'Activity not found'},
                                status=status.HTTP_404_NOT_FOUND)

            cards = Card.objects.filter(activity=activity)
            user_cards = UserCard.objects.filter(
                card__in=cards, user_id=user_id)

            response_data = {
                'recent_card_id': last_card_id,
                'cards': []
            }

            for card in cards:
                serialized_card = CardSerializer(card).data

                user_card = user_cards.filter(card=card).first()
                if user_card:
                    serialized_user_card = UserCardSerializer(user_card).data
                    serialized_card['user_card_progress'] = serialized_user_card

                questions = Question.objects.filter(card=card)
                serialized_questions = []
                for question in questions:
                    serialized_question = QuestionSerializer(question).data

                    options = Option.objects.filter(question=question)
                    serialized_options = OptionSerializer(
                        options, many=True).data
                    if serialized_options:
                        serialized_question['options'] = serialized_options

                    answers = Answer.objects.filter(
                        question=question, user_id=user_id)
                    serialized_answers = AnswerSerializer(
                        answers, many=True).data
                    serialized_question['answers'] = serialized_answers

                    serialized_questions.append(serialized_question)

                serialized_card['questions'] = serialized_questions
                response_data['cards'].append(serialized_card)

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserActivityProgressList(APIView):
    
    permission_classes = [IsAuthenticatedVerifiedActive, IsAdminOrOrganizerOrUser]

    @swagger_auto_schema(
        operation_description="Retrieve the user's activity progress for a batch.",
        responses={
            200: batch_activity_response_schema,
            400: 'Bad Request',
            404: 'Not Found',
            500: 'Internal Server Error'
        },
        manual_parameters=[
        openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                description="Bearer token",
                type=openapi.TYPE_STRING,
                required=True,
                examples={
                    'Bearer Token': {
                        'value': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzE5MzQ1MzYzLCJpYXQiOjE3MTkzNDE3NjMsImp0aSI6IjRkNTc0NjY3ZjQyZjQxZDE5NzcyOWNiMzg5MTIyYjU2IiwidXNlcl9pZCI6M30.ygESn-3hdcd-3x1HH0z9Rdpx2J3WZpce8PI3OZlRfRQ'
                    }
                }
            )
        ],
        )
    def get(self, request, user_id, batch_id):
        try:
            if (request.user.id != user_id):
                return Response(
                    {'error': 'Invalid Authentication Credentials'} 
                )
            
            latest_user_activity = UserActivity.objects.filter(
                user_id=user_id, activity__batch_id=batch_id).order_by('-updated_at').first()
            first_user_activity = Activity.objects.filter(
                batch_id=batch_id).order_by('created_at').first()
            last_activity_id = latest_user_activity.activity.id if latest_user_activity else (
                first_user_activity.id if first_user_activity else None)

            if not last_activity_id:
                return Response(
                    {'error': 'No UserActivity found for the user'}, status=status.HTTP_404_NOT_FOUND)

            try:
                batch = Batch.objects.get(id=batch_id)
            except Batch.DoesNotExist:
                return Response({'error': 'Batch not found'},
                                status=status.HTTP_404_NOT_FOUND)

            activities = Activity.objects.filter(batch=batch)

            response_data = {
                'current_activity_id': last_activity_id,
                'activities': []
            }

            user_activities = UserActivity.objects.filter(
                user_id=user_id, activity__in=activities)
            for activity in activities:
                serialized_activity = ActivitySerializer(activity).data

                user_activity = user_activities.filter(
                    activity=activity).first()
                if user_activity:
                    serialized_user_activity = UserActivitySerializer(
                        user_activity).data
                    serialized_activity['user_activity_progress'] = serialized_user_activity

                response_data['activities'].append(serialized_activity)

            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
