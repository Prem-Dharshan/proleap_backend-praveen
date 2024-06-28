from django.urls import path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

from .views import (
    UserListAPIView,
    UserDetailAPIView,
    SignInAPIView,
    BatchListCreateAPIView,
    BatchDetailAPIView,
    UserBatchListCreateAPIView,
    UserBatchDetailAPIView,
    BatchUserListAPIView,
    ActivityListCreateAPIView,
    ActivityDetailAPIView,
    UserActivityListCreateAPIView,
    UserActivityDetailAPIView,
    CardListCreateAPIView,
    CardDetailAPIView,
    UserCardListCreateAPIView,
    UserCardDetailAPIView,
    QuestionListCreateAPIView,
    QuestionDetailAPIView,
    OptionListCreateAPIView,
    OptionDetailAPIView,
    AnswerListCreateAPIView,
    AnswerDetailAPIView,
    UserRegister,
    VerifyEmail,
    UserCardQuestionProgress,
    UserActivityProgressList)

schema_view = get_schema_view(
    openapi.Info(
        title="ProLeap API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="proleap.ewhiz@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [

    path(
        'swagger<format>/',
        schema_view.without_ui(
            cache_timeout=0),
        name='schema-json'),
    path(
        'swagger/',
        schema_view.with_ui(
            'swagger',
            cache_timeout=0),
        name='schema-swagger-ui'),
    path(
        'redoc/',
        schema_view.with_ui(
            'redoc',
            cache_timeout=0),
        name='schema-redoc'),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('signin/', SignInAPIView.as_view(), name='auth'),

    # URLs for User APIs
    path('users/', UserListAPIView.as_view(), name='users'),
    path('users/<int:id>/', UserDetailAPIView.as_view(), name='users'),

    # URLs for Batch APIs
    path(
        'batches/',
        BatchListCreateAPIView.as_view(),
        name='batch-list-create'),
    path(
        'batches/<int:pk>/',
        BatchDetailAPIView.as_view(),
        name='batch-detail'),

    # URLs for UserBatch APIs
    path(
        'userbatches/',
        UserBatchListCreateAPIView.as_view(),
        name='user-batch-list-create'),
    path(
        'userbatches/<int:pk>/',
        UserBatchDetailAPIView.as_view(),
        name='user-batch-detail'),
    path(
        'batches-users/',
        BatchUserListAPIView.as_view(),
        name='batch-user-list'),

    # URLs for Activity APIs
    path(
        'activities/',
        ActivityListCreateAPIView.as_view(),
        name='activity-list-create'),
    path(
        'activities/<int:pk>/',
        ActivityDetailAPIView.as_view(),
        name='activity-detail'),

    # URLs for UserActivity APIs
    path(
        'user-activities/',
        UserActivityListCreateAPIView.as_view(),
        name='user-activity-list-create'),
    path(
        'user-activities/<int:pk>/',
        UserActivityDetailAPIView.as_view(),
        name='user-activity-detail'),

    # URLs for Cards APIs
    path('cards/', CardListCreateAPIView.as_view(), name='card-list-create'),
    path('cards/<int:pk>/', CardDetailAPIView.as_view(), name='card-detail'),

    # URLs for UserCard APIs
    path(
        'user-cards/',
        UserCardListCreateAPIView.as_view(),
        name='user-card-list-create'),
    path(
        'user-cards/<int:pk>/',
        UserCardDetailAPIView.as_view(),
        name='user-card-detail'),

    path(
        'questions/',
        QuestionListCreateAPIView.as_view(),
        name='question-list-create'),
    path(
        'questions/<int:pk>/',
        QuestionDetailAPIView.as_view(),
        name='question-detail'),

    path(
        'options/',
        OptionListCreateAPIView.as_view(),
        name='option-list-create'),
    path(
        'options/<int:pk>/',
        OptionDetailAPIView.as_view(),
        name='option-detail'),

    path(
        'answers/',
        AnswerListCreateAPIView.as_view(),
        name='answer-list-create'),
    path(
        'answers/<int:pk>/',
        AnswerDetailAPIView.as_view(),
        name='answer-detail'),

    path('upload-csv/', UserRegister.as_view(), name='upload_users_csv'),

    path('register/', UserRegister.as_view(), name='user-register'),
    path('verify/<str:token>/', VerifyEmail.as_view(), name='verify-email'),

    path(
        'user/<int:user_id>/activity/<int:activity_id>/',
        UserCardQuestionProgress.as_view(),
        name='user-card-question-detail'),
    path('user/<int:user_id>/batch/<int:batch_id>/activities/',
         UserActivityProgressList.as_view(), name='user-activities-detail'),
]
