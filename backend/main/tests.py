from decimal import Decimal
from django.utils import timezone
import pytest
from django.urls import reverse
from main.models import User, Wallet, Cryptocurrency, TradingPair, Order, Transaction


# 1. Проверяет, что нельзя создать Ордер без обязательных полей
@pytest.mark.django_db
def test_order_validation_fail():
    with pytest.raises(Exception):
        Order.objects.create()


# 2. Проверяет правильное хранение и отображение баланса
@pytest.mark.django_db
def test_wallet_balance_format():
    user = User.objects.create_user(email="u@mail.com", password="123", name="Имя", role="user")
    crypto = Cryptocurrency.objects.create(name="BTC", symbol="BTC", network="Bitcoin", price=Decimal("30000"))
    wallet = Wallet.objects.create(user=user, crypto=crypto, balance=Decimal("5.0"))
    assert str(wallet.balance) == "5.0"


# 3. Проверяет работу представления списка ордеров (OrderListView)
@pytest.mark.django_db
def test_order_list_view(client):
    user = User.objects.create_user(email="test@mail.com", password="123", name="Имя", role="user")
    crypto1 = Cryptocurrency.objects.create(name="BTC", symbol="BTC", network="Bitcoin", price=Decimal("30000"))
    crypto2 = Cryptocurrency.objects.create(name="USDT", symbol="USDT", network="Ethereum", price=Decimal("1.00"))
    pair = TradingPair.objects.create(base_currency=crypto1, quote_currency=crypto2)
    Order.objects.create(user=user, trading_pair=pair, type="buy", price=20000, volume=0.5, status="pending")
    
    url = reverse("order-list")
    response = client.get(url)
    assert response.status_code == 200


# 4. Проверяет, что ордер сохраняется корректно с нужными полями
@pytest.mark.django_db
def test_order_creation():
    user = User.objects.create_user(email="test@mail.com", password="123", name="Имя", role="user")
    crypto1 = Cryptocurrency.objects.create(name="BTC", symbol="BTC", network="Bitcoin", price=Decimal("30000"))
    crypto2 = Cryptocurrency.objects.create(name="USDT", symbol="USDT", network="Ethereum", price=Decimal("1.00"))
    pair = TradingPair.objects.create(base_currency=crypto1, quote_currency=crypto2)
    order = Order.objects.create(user=user, trading_pair=pair, type="buy", price=15000, volume=1.0, status="pending")
    assert order.price == 15000
    assert order.type == "buy"


# 5. Проверяет фильтрацию по статусу ордера
@pytest.mark.django_db
def test_order_filter_by_status(client):
    user = User.objects.create_user(email="user@mail.com", password="123", name="Имя", role="user")
    crypto1 = Cryptocurrency.objects.create(name="BTC", symbol="BTC", network="Bitcoin", price=Decimal("30000"))
    crypto2 = Cryptocurrency.objects.create(name="USDT", symbol="USDT", network="Ethereum", price=Decimal("1.00"))
    pair = TradingPair.objects.create(base_currency=crypto1, quote_currency=crypto2)

    Order.objects.create(user=user, trading_pair=pair, type="buy", price=20000, volume=1, status="completed")
    Order.objects.create(user=user, trading_pair=pair, type="sell", price=21000, volume=1, status="pending")

    url = reverse("order-list") + "?status=completed"
    response = client.get(url)
    assert response.status_code == 200
    assert "completed" in str(response.content)


# 6. Проверяет метод __str__ модели Cryptocurrency
@pytest.mark.django_db
def test_crypto_str():
    crypto = Cryptocurrency.objects.create(name="Bitcoin", symbol="BTC", network="Bitcoin", price=Decimal("30000"))
    assert str(crypto) == "Bitcoin (BTC)"


# 7. Проверяет корректность создания транзакции
@pytest.mark.django_db
def test_transaction_creation():
    user = User.objects.create_user(email="u@mail.com", password="123", name="Имя", role="user")
    crypto1 = Cryptocurrency.objects.create(name="BTC", symbol="BTC", network="Bitcoin", price=Decimal("30000"))
    crypto2 = Cryptocurrency.objects.create(name="USDT", symbol="USDT", network="Ethereum", price=Decimal("1"))
    pair = TradingPair.objects.create(base_currency=crypto1, quote_currency=crypto2)

    order = Order.objects.create(user=user, trading_pair=pair, type="buy", price=20000, volume=1, status="completed")

    tx = Transaction.objects.create(
        order=order,
        counter_order=None,
        user=user,
        crypto=crypto1,
        type="trade",
        amount=Decimal("20000"),
        fee=Decimal("20"),
        total_amount=Decimal("19980"),
        status="completed",
        timestamp=timezone.now()
    )
    assert tx.total_amount == Decimal("19980")


# 8. Проверяет вход пользователя
@pytest.mark.django_db
def test_user_login(client):
    user = User.objects.create_user(email="user@mail.com", password="user", name="Пользователь", role="user")
    logged_in = client.login(email="user@mail.com", password="user")
    assert logged_in is True


# 9. Проверяет создание криптовалюты
@pytest.mark.django_db
def test_crypto_creation():
    crypto = Cryptocurrency.objects.create(name="Bitcoin", symbol="BTC", network="Bitcoin", price=Decimal("30000"))
    assert str(crypto) == "Bitcoin (BTC)"


# 10. Проверяет обновление баланса кошелька
@pytest.mark.django_db
def test_wallet_balance_update():
    user = User.objects.create_user(email="wallet@mail.com", password="123", name="Имя", role="user")
    crypto = Cryptocurrency.objects.create(name="BTC", symbol="BTC", network="Bitcoin", price=Decimal("30000"))
    wallet = Wallet.objects.create(user=user, crypto=crypto, balance=Decimal("5.0"))
    wallet.balance += Decimal("2.0")
    wallet.save()
    wallet.refresh_from_db()
    assert wallet.balance == Decimal("7.0")
