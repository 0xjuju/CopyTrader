
from django.urls import path
from blockchain import views


urlpatterns = [
    path("wallet", views.wallet_hook, name="wallet_webhook")
]



