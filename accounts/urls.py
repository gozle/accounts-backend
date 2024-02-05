import oauth2_provider.views as oauth2_views
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from users.views import ApiEndpoint
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView


# OAuth2 provider endpoints
oauth2_endpoint_views = [
    path('authorize/', oauth2_views.AuthorizationView.as_view(), name="authorize"),
    path('token/', oauth2_views.TokenView.as_view(), name="token"),
    path('revoke-token/', oauth2_views.RevokeTokenView.as_view(), name="revoke-token"),
]

if settings.DEBUG:
    # OAuth2 Application Management endpoints
    oauth2_endpoint_views += [
        path('applications/', oauth2_views.ApplicationList.as_view(), name="list"),
        path('applications/register/', oauth2_views.ApplicationRegistration.as_view(), name="register"),
        path('applications/<pk>/', oauth2_views.ApplicationDetail.as_view(), name="detail"),
        path('applications/<pk>/delete/', oauth2_views.ApplicationDelete.as_view(), name="delete"),
        path('applications/<pk>/update/', oauth2_views.ApplicationUpdate.as_view(), name="update"),
    ]

    # OAuth2 Token Management endpoints
    oauth2_endpoint_views += [
        path('authorized-tokens/', oauth2_views.AuthorizedTokensListView.as_view(), name="authorized-token-list"),
        path('authorized-tokens/<pk>/delete/', oauth2_views.AuthorizedTokenDeleteView.as_view(),
             name="authorized-token-delete"),
    ]

urlpatterns = [
    # OAuth 2 endpoints:
    path('o/', include((oauth2_endpoint_views, 'oauth2_provider'), namespace="oauth2_provider")),

    # JWT Token Endpoints
    path('auth/token', TokenObtainPairView.as_view(), name='token_jwt_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_jwt_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_jwt_verify'),

    # Admin urls
    path('jet/', include('jet.urls', 'jet')),  # Django JET URLS
    path('jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),  # Django JET dashboard URLS
    path('admin/', admin.site.urls),

    # Auth
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('api/hello', ApiEndpoint.as_view()),
]
