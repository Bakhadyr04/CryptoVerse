from rest_framework import serializers
from main.models import Cryptocurrency, Order, Promotion, TradingPair, Transaction, User, UserPromotion, Wallet
from django.contrib.auth import get_user_model

class CryptocurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Cryptocurrency
        fields = '__all__'

# class PromotionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Promotion
#         fields = ['id', 'title', 'description', 'start_date', 'end_date']

class PromotionSerializer(serializers.ModelSerializer):
    participants = serializers.SerializerMethodField()
    image = serializers.ImageField(required=False)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Promotion
        fields = ['id', 'title', 'description', 'start_date', 'end_date', 'participants', 'image', 'image_url']

    def get_participants(self, obj):
        from .serializers import UserSimpleSerializer
        user_promotions = obj.userpromotion_set.select_related('user')
        return UserSimpleSerializer([up.user for up in user_promotions], many=True).data
    
    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name']

class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name']

# Сериализатор только для записи (POST/PUT) — использует ID
class UserPromotionWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPromotion
        fields = ['id', 'user', 'promotion', 'participation_date']

# Сериализатор только для чтения (GET) — вложенные объекты
class UserPromotionReadSerializer(serializers.ModelSerializer):
    user = UserSimpleSerializer()
    promotion = PromotionSerializer()

    class Meta:
        model = UserPromotion
        fields = ['id', 'user', 'promotion', 'participation_date']


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

    def create(self, validated_data):
        trading_pair = validated_data['trading_pair']
        validated_data['price'] = trading_pair.price  # Автоматически подставляем цену
        return super().create(validated_data)
    


# Криптовалюты
class CryptocurrencySerializer(serializers.ModelSerializer):
    # display = serializers.SerializerMethodField()

    class Meta:
        model = Cryptocurrency
        # fields = ['display']
        fields = ['id', 'name', 'symbol', 'network', 'price']

    def get_display(self, obj):
        return str(obj)

# class CryptocurrencySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Cryptocurrency
#         fields = ['name', 'symbol']

# Торговые пары
class TradingPairSerializer(serializers.ModelSerializer):
    base_currency = CryptocurrencySerializer()
    quote_currency = CryptocurrencySerializer()

    class Meta:
        model = TradingPair
        fields = ['base_currency', 'quote_currency']

# Ордеры
class OrderSerializer(serializers.ModelSerializer):
    # user = serializers.StringRelatedField()
    # trading_pair = TradingPairSerializer()
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    trading_pair = serializers.PrimaryKeyRelatedField(queryset=TradingPair.objects.all())
    total_value = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'user', 'trading_pair', 'type', 'price',
                  'volume', 'total_value', 'status', 'created_at']

    def get_total_value(self, obj):
        return obj.price * obj.volume

# Транзакции # Использование SerializerMethodField
class TransactionSerializer(serializers.ModelSerializer):
    # user = serializers.StringRelatedField()
    # crypto = CryptocurrencySerializer()
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    crypto = serializers.PrimaryKeyRelatedField(queryset=Cryptocurrency.objects.all())
    timestamp = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Transaction
        fields = ['id', 'order', 'user', 'crypto', 'type', 'amount', 'fee', 'total_amount', 'status', 'timestamp']
    
    extra_kwargs = {'order': {'write_only': True}}

    def create(self, validated_data):
        user = validated_data['user']

        order = Order.objects.filter(user=user, status='pending').last()

        if not order:
            raise serializers.ValidationError("Order not found for user.")

        validated_data['order'] = order
        return super().create(validated_data)

# Акции
class PromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotion
        fields = ['title', 'start_date', 'end_date']

# Пользователи участвующие в акции
class UserWithPromotionsSerializer(serializers.ModelSerializer):
    promotions = PromotionSerializer(many=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'role', 'promotions']



# Передача данных через context. Конвертируем цену из USD в RUB
class CryptoPriceSerializer(serializers.ModelSerializer):
    price_converted = serializers.SerializerMethodField()

    class Meta:
        model = Cryptocurrency
        fields = ['id', 'name', 'symbol', 'price', 'price_converted']

    def get_price_converted(self, obj):
        currency = self.context.get('fiat_currency', 'USD').upper()
        rate = {
            'USD': 1,
            'EUR': 0.9,
            'RUB': 90,
        }.get(currency, 1)
        return round(obj.price * 90, 2)


# Добавили price_converted в fields. Аннотированное поле из queryset подтягивается само
class CryptoPriceAnnotatedSerializer(serializers.ModelSerializer):
    price_converted = serializers.FloatField()

    class Meta:
        model = Cryptocurrency
        fields = ["id", "name", "symbol", "price", "price_converted"]



# Передаём аннотацию avg_price для среднего курса криптовалюты за период
class CryptoAvgPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cryptocurrency
        fields = ["id", "name", "symbol", "avg_price"]


# Передаём аннотацию trade_volume для общиего объёма торгов по каждой криптовалюте
class CryptoTradeVolumeSerializer(serializers.ModelSerializer):
    trade_volume = serializers.FloatField()

    class Meta:
        model = Cryptocurrency
        fields = ['id', 'name', 'symbol', 'trade_volume']

    def get_trade_volume(self, obj):
        return float(obj.trade_volume or 0)
    
    
# 
class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['id', 'user', 'crypto', 'balance']


# 
User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'name', 'password', 'password2')
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user