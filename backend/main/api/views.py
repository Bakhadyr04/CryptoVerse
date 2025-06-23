from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from main.models import Cryptocurrency, Order, Transaction, UserPromotion, User, Promotion, Cryptocurrency, Wallet
from .serializers import CryptoPriceSerializer, CryptocurrencySerializer, OrderSerializer, CryptoPriceAnnotatedSerializer, CryptoAvgPriceSerializer, CryptoTradeVolumeSerializer, WalletSerializer
from main.api.serializers import UserPromotionReadSerializer, UserPromotionWriteSerializer, UserSerializer, PromotionSerializer, TransactionSerializer, UserWithPromotionsSerializer, OrderSerializer, RegisterSerializer
from django.db.models import F, ExpressionWrapper, FloatField, Value, Avg, Sum, Q
from datetime import timedelta
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from main.api.filters import OrderFilter
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt

class CryptocurrencyViewSet(viewsets.ModelViewSet):
    queryset = Cryptocurrency.objects.all()
    serializer_class = CryptocurrencySerializer
    permission_classes = [AllowAny]

class UserPromotionViewSet(viewsets.ModelViewSet):
    # Использование select_related для ForeignKey (многие к одному)
    queryset = UserPromotion.objects.select_related('user', 'promotion')   # http://localhost:8000/api/user-promotions/
    # queryset = UserPromotion.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return UserPromotionWriteSerializer
        return UserPromotionReadSerializer
    
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class PromotionViewSet(viewsets.ModelViewSet):
    # queryset = Promotion.objects.all()
    # Использование prefetch_related для обратной связи (один ко многим или многие ко многим)
    queryset = Promotion.objects.prefetch_related('userpromotion_set__user') # http://localhost:8000/api/promotions/
    serializer_class = PromotionSerializer



# Получение списка ордеров с информацией о пользователях
class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Order.objects.select_related('user', 'trading_pair__base_currency', 'trading_pair__quote_currency')
    serializer_class = OrderSerializer


# Получение списка транзакций с информацией о криптовалютах
class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.select_related('user', 'crypto')
    serializer_class = TransactionSerializer

    permission_classes = [IsAuthenticated]


# Получение списка пользователей и акций, в которых они участвуют
class UserPromotionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.prefetch_related('promotions')
    serializer_class = UserWithPromotionsSerializer
    


# Передача данных в сериализатор через контекст
class CryptoPriceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Cryptocurrency.objects.all()
    serializer_class = CryptoPriceSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['fiat_currency'] = self.request.query_params.get('currency', 'USD')
        return context


# Используем аннотацию price_converted, чтобы вычислить цену в нужной валюте
class CryptoPriceAnnotatedViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CryptoPriceAnnotatedSerializer

    def get_queryset(self):
        currency = self.request.query_params.get("currency", "USD").upper()
        rates = {"USD": 1, "EUR": 0.9, "RUB": 90}
        rate = rates.get(currency, 1)
        
        return Cryptocurrency.objects.annotate(
            price_converted=ExpressionWrapper(
                F("price") * Value(rate),
                output_field=FloatField()
            )
        )



# Средний курс криптовалюты за период
class CryptoAvgPriceViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CryptoAvgPriceSerializer

    def get_queryset(self):
        days = int(self.request.query_params.get("days", 30))
        date_threshold = timezone.now() - timedelta(days=days)

        return Cryptocurrency.objects.annotate(
            avg_price=Avg(
                "order__price",
                filter=Q(order__created_at__gte=date_threshold)
            )
        )

# Общий объём торгов по каждой криптовалюте
class CryptoTradeVolumeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CryptoTradeVolumeSerializer

    def get_queryset(self):
        return Cryptocurrency.objects.annotate(
            trade_volume=Sum(
                'base_pairs__orders__volume',
                filter=Q(base_pairs__orders__status='completed')
            ) + Sum(
                'quote_pairs__orders__volume',
                filter=Q(quote_pairs__orders__status='completed')
            )
        )



# Фильтрация через DjangoFilterBackend
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = OrderFilter

    
# 
class WalletViewSet(viewsets.ModelViewSet):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer


# 
User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


# 
@require_GET
def cryptocurrency_list(request):
    """
    Возвращает список криптовалют с названием, символом и ценой.
    """
    data = list(Cryptocurrency.objects.values("id", "name", "symbol", "price"))
    return JsonResponse(data, safe=False)

@csrf_exempt
def api_cryptocurrencies(request):
    """
    Возвращает JSON со всеми криптовалютами.
    """
    data = list(Cryptocurrency.objects.values("id", "name", "symbol", "price"))
    return JsonResponse(data, safe=False)