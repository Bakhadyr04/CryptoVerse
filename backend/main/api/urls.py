from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import CryptoAvgPriceViewSet, CryptoPriceViewSet, CryptoTradeVolumeViewSet, CryptocurrencyViewSet, OrderViewSet, PromotionViewSet, TransactionViewSet, UserPromotionViewSet, UserViewSet, CryptoPriceAnnotatedViewSet, WalletViewSet, api_cryptocurrencies, cryptocurrency_list

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET

router = DefaultRouter()
                                                              # http://localhost:8000/api/cryptocurrencies/   - API (криптовалюты)
router.register(r'cryptocurrencies', CryptocurrencyViewSet)   # http://localhost:3000/cryptocurrencies        - САЙТ (криптовалюты)
router.register(r'user-promotions', UserPromotionViewSet)     # http://localhost:3000/user-promotions         - САЙТ (пользователи участвующие в акции)
router.register(r'users', UserViewSet, basename='users_view') # http://localhost:8000/api/users/              - API (пользователи)
router.register(r'promotions', PromotionViewSet)              # http://localhost:8000/api/promotions/         - API (акции)

router.register(r'orders', OrderViewSet)                      # http://localhost:8000/api/orders/             - Получение списка ордеров с информацией о пользователях
router.register(r'transactions', TransactionViewSet)          # http://localhost:8000/api/transactions/       - Получение списка транзакций с информацией о криптовалютах
router.register(r'users-promotions', UserPromotionViewSet,    # http://localhost:8000/api/users-promotions/   - Получение списка пользователей и акций, в которых они участвуют
                basename='user_promotions') 

router.register(r'crypto-prices', CryptoPriceViewSet,         # http://localhost:8000/api/crypto-prices/      - Получение конвертированной цены (USD в RUB)
                basename='crypto-price') 
router.register(r'crypto-price-annotated',                    # http://localhost:8000/api/crypto-price-annotated/?currency=RUB - Получение конвертированной цены (USD в RUB)
                CryptoPriceAnnotatedViewSet,
                basename='crypto-price-annotated')

router.register(r'crypto-prices-average',                     # http://localhost:8000/api/crypto-prices-average/ - Средний курс криптовалюты за определенный период
                CryptoPriceAnnotatedViewSet,
                basename='crypto-price-average') 
router.register(r'crypto-trade-volumes',                      # http://localhost:8000/api/crypto-trade-volumes/ - Общим объём торгов для каждой криптовалюты
                CryptoTradeVolumeViewSet,
                basename='crypto-trade-volumes')

router.register(r'wallets', WalletViewSet)

urlpatterns = [
    path("api/cryptocurrencies/", csrf_exempt(api_cryptocurrencies), name="api_cryptocurrencies"),
] + router.urls

urlpatterns = router.urls
