from django.urls import path
from .views import RegisterView, CurrentUserView, LogoutView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='account_register'),
    path('me/', CurrentUserView.as_view(), name='account_current_user'),
    path('logout/', LogoutView.as_view(), name='account_logout'),
]
