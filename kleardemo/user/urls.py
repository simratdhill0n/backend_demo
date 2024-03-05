from django.urls import path
from .views import create_user, login, search_address, create_wallet, get_wallet_info, make_payment_api

urlpatterns = [
    path('signup/', create_user, name='user_signup'),
    path('login/', login, name='login'),
    path('search/', search_address, name='search'),
    path('create_wallet/', create_wallet, name='create_wallet'),
    path('get_wallet_info/', get_wallet_info, name='get_wallet_info'),
    path('make_payment/', make_payment_api, name='make_payment'),
]