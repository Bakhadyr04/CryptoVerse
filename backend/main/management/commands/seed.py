from decimal import ROUND_DOWN, Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.exceptions import ValidationError
from main.models import *
from faker import Faker
import random
import secrets

class Command(BaseCommand):
    help = 'Создание реалистичных и связанных тестовых данных'

    def handle(self, *args, **kwargs):
        fake = Faker('ru_RU')

        # Криптовалюты
        crypto_data = [
            ('Bitcoin', 'BTC', 'Bitcoin'),
            ('Ethereum', 'ETH', 'Ethereum'),
            ('Tether', 'USDT', 'Ethereum'),
            ('BNB', 'BNB', 'BNB Chain'),
            ('Cardano', 'ADA', 'Cardano'),
            ('Solana', 'SOL', 'Solana'),
            ('Ripple', 'XRP', 'Ripple'),
            ('Polkadot', 'DOT', 'Polkadot'),
            ('Litecoin', 'LTC', 'Litecoin'),
            ('Dogecoin', 'DOGE', 'Dogecoin')
        ]

        cryptos = []
        for name, symbol, network in crypto_data:
            price = Decimal(str(random.uniform(0, 50000))).quantize(Decimal('0.00000001'), rounding=ROUND_DOWN)
            crypto = Cryptocurrency(name=name, symbol=symbol, network=network, price=price)
            try:
                crypto.full_clean()
                crypto.save()
                cryptos.append(crypto)
            except ValidationError as e:
                print(f"❌ Ошибка при создании {name}: {e}")

        if not cryptos:
            self.stdout.write(self.style.ERROR("⛔ Не удалось создать ни одной криптовалюты — остановка генерации"))
            return

        # Пользователи
        users = []
        for i in range(10):
            role = 'admin' if i == 0 else 'user'
            user = User.objects.create_user(
                email=fake.unique.email(),
                password='qwerty123',
                name=fake.name(),
                role=role
            )
            user.last_login = timezone.now()
            user.save()
            users.append(user)

        # Кошельки
        for user in users:
            crypto = random.choice(cryptos)
            Wallet.objects.get_or_create(
                user=user,
                crypto=crypto,
                defaults={
                    'balance': 100000,
                    'last_transaction_date': timezone.now()
                }
            )

        # Торговые пары
        trading_pairs = []
        for i in range(len(cryptos) - 1):
            base = cryptos[i]
            quote = cryptos[i + 1]
            trading_pairs.append(TradingPair.objects.create(
                base_currency=base,
                quote_currency=quote
            ))

        # Ордера
        orders = []
        for i in range(10):
            user = users[i % len(users)]
            pair = trading_pairs[i % len(trading_pairs)]
            order = Order.objects.create(
                user=user,
                trading_pair=pair,
                type='buy' if i % 2 == 0 else 'sell',
                price=20000 + i * 100,
                volume=0.5 + i * 0.1,
                status=random.choice(['pending', 'completed', 'cancelled', 'partially_completed'])
            )
            orders.append(order)

        # Транзакции
        transactions = []
        for i in range(len(orders) - 1):
            order = orders[i]
            counter_order = orders[i + 1]
            amount = order.volume * order.price
            fee = round(amount * 0.001, 8)
            total = amount - fee

            # ✅ Убедиться, что кошелек существует
            wallet, _ = Wallet.objects.get_or_create(
                user=order.user,
                crypto=crypto,
                defaults={
                    'balance': 100000,  # достаточно для вывода
                    'last_transaction_date': timezone.now()
                }
            )

            tx = Transaction.objects.create(
                order=order,
                counter_order=counter_order,
                user=order.user,
                crypto=order.trading_pair.base_currency,
                type=random.choice(['deposit', 'withdrawal', 'trade']),
                amount=amount,
                fee=fee,
                total_amount=total,
                status=random.choice(['pending', 'completed', 'cancelled']),
                timestamp=timezone.now(),
                description='Исполнение ордера',
                is_refunded=False
            )
            transactions.append(tx)

        # История транзакций
        for tx in transactions:
            TransactionHistory.objects.create(
                transaction=tx,
                amount=tx.amount,
                symbol=tx.crypto.symbol,
                type=tx.type,
                status=tx.status,
                changed_at=timezone.now(),
                description=tx.description
            )

        # Тикеты поддержки
        for i in range(10):
            SupportTicket.objects.create(
                user=users[i % len(users)],
                subject=f'Проблема с транзакцией {i}',
                status=random.choice(['open', 'closed'])
            )

        # Акции
        promotions = []
        for i in range(10):
            promo = Promotion.objects.create(
                title=f'Акция {i}',
                description='Получите бонус при пополнении счёта!',
                start_date=timezone.now(),
                end_date=timezone.now() + timezone.timedelta(days=15)
            )
            promotions.append(promo)

        # Участие в акциях
        for i in range(10):
            UserPromotion.objects.create(
                user=users[i % len(users)],
                promotion=promotions[i % len(promotions)],
                participation_date=timezone.now()
            )

        # Страницы
        pages = []
        for i in range(10):
            pages.append(Page.objects.create(
                page_name=f'страница_{i}',
                can_view=(i % 2 == 0)
            ))

        # Разрешения
        guest_permissions = []
        for page in pages:
            guest_permissions.append(GuestPermission.objects.create(
                page_name=page.page_name,
                can_view=page.can_view,
                can_register=True,
                can_login=False
            ))

        # Действия гостей
        guest_actions = []
        for i in range(10):
            guest_actions.append(GuestAction.objects.create(
                action_name=f'действие_{i}',
                can_execute=(i % 2 == 0),
                description='Пример действия'
            ))

        # Связь разрешений и действий
        for i in range(10):
            GuestPermissionsActions.objects.create(
                guest_permission=guest_permissions[i],
                guest_action=guest_actions[i]
            )

        # Сессии гостей
        for i in range(10):
            token = secrets.token_hex(16)
            GuestSession.objects.create(
                session_token=token,
                ip_address=f'192.168.1.{i+1}',
                last_activity=timezone.now()
            )

        self.stdout.write(self.style.SUCCESS('✅ Данные успешно созданы!'))
