from datetime import timedelta
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.forms import ValidationError
from django.core.validators import validate_email
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import secrets

# Генерирует 32-символьный hex токен
def generate_guest_token() -> str:
    """
    Генерирует 32-символьный случайный hex-токен для гостевой сессии.

    Returns:
        Строка — токен из 32 символов.
    """
    return secrets.token_hex(16)

class UserManager(BaseUserManager):
    def create_user(self, email: str, password: str | None = None, **extra_fields) -> "User":
        """
        Создаёт обычного пользователя.

        Args:
            email: Email пользователя.
            password: Пароль.
            extra_fields: Дополнительные поля.

        Returns:
            Объект User.
        """
        if not email:
            raise ValueError('У пользователя должен быть email')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str | None = None, **extra_fields) -> "User":
        """
        Создаёт суперпользователя.

        Args:
            email: Email суперпользователя.
            password: Пароль.
            extra_fields: Дополнительные поля.

        Returns:
            Объект User.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser должен иметь is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser должен иметь is_superuser=True')

        return self.create_user(email, password, **extra_fields)
    
    def active_last_24h(self) -> models.QuerySet:
        """
        Получает пользователей, активных за последние 24 часа.

        Returns:
            QuerySet активных пользователей.
        """
        since = timezone.now() - timedelta(hours=24)
        return self.get_queryset().filter(last_login__gte=since)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Кастомная модель пользователя с ролями (user, admin), email-авторизацией и базовыми полями профиля.
    """
    email = models.EmailField(unique=True, verbose_name=_("Email"))
    password = models.CharField(max_length=128, verbose_name=_("Пароль"))
    name = models.CharField(max_length=100, verbose_name=_("Имя"))
    ROLE_CHOICES = [
        ('user', _('Пользователь')),
        ('admin', _('Администратор')),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user', verbose_name=_("Роль"))
    is_active = models.BooleanField(default=True, verbose_name=_("Активен"))
    is_staff = models.BooleanField(default=False, verbose_name=_("Сотрудник"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата регистрации"))
    last_login = models.DateTimeField(null=True, blank=True, verbose_name=_("Последний вход"))

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ['-created_at']

    # Валидация email
    def clean(self) -> None:
        """
        Валидация email пользователя.

        Raises:
            ValidationError: Если email некорректный.
        """
        validate_email(self.email)

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"


class GuestSession(models.Model):
    """
    Модель, представляющая гостевую сессию пользователя по IP-адресу и токену.
    """
    # user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_("Пользователь"))
    session_token = models.CharField(max_length=255, default=generate_guest_token, verbose_name=_("Токен сессии"))
    ip_address = models.GenericIPAddressField(verbose_name=_("IP-адрес"))
    last_activity = models.DateTimeField(verbose_name=_("Последняя активность"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Создано"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Обновлено"))

    class Meta:
        verbose_name = "Гостевая сессия"
        verbose_name_plural = "Гостевые сессии"
        ordering = ['-created_at']

    def __str__(self):
        return f"Session {self.id}"


class Page(models.Model):
    """
    Представляет страницу приложения, которую можно разрешить к просмотру.
    """
    page_name = models.CharField(max_length=255, verbose_name=_("Название страницы"))
    can_view = models.BooleanField(default=True, verbose_name=_("Можно просматривать"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Создано"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Обновлено"))

    class Meta:
        verbose_name = "Страница"
        verbose_name_plural = "Страницы"
        ordering = ['-created_at']

    def __str__(self):
        return self.page_name


class GuestPermission(models.Model):
    """
    Гостевое разрешение: определяет, какие страницы доступны без авторизации и какие действия разрешены.
    """
    page_name = models.CharField(max_length=255, verbose_name=_("Имя страницы"))
    can_view = models.BooleanField(default=True, verbose_name=_("Можно просматривать"))
    can_register = models.BooleanField(default=False, verbose_name=_("Можно зарегистрироваться"))
    can_login = models.BooleanField(default=False, verbose_name=_("Можно войти"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Создано"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Обновлено"))

    # Добавляем ManyToMany через промежуточную модель
    actions = models.ManyToManyField(
        'GuestAction',
        through='GuestPermissionsActions',
        related_name='permissions',
        verbose_name=_("Доступные действия")
    )

    class Meta:
        verbose_name = "Гостевое разрешение"
        verbose_name_plural = "Гостевые разрешения"
        ordering = ['-created_at']

    def __str__(self):
        return self.page_name


class GuestAction(models.Model):
    """
    Действие, которое может быть разрешено гостю — например, регистрация или вход.
    """
    action_name = models.CharField(max_length=255, verbose_name=_("Имя действия"))
    can_execute = models.BooleanField(default=True, verbose_name=_("Можно выполнять"))
    description = models.TextField(blank=True, verbose_name=_("Описание"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Создано"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Обновлено"))

    class Meta:
        verbose_name = "Гостевое действие"
        verbose_name_plural = "Гостевые действия"
        ordering = ['-created_at']

    def __str__(self):
        return self.action_name


class GuestPermissionsActions(models.Model):
    """
    Промежуточная модель между GuestPermission и GuestAction, указывающая разрешённые действия.
    """
    guest_permission = models.ForeignKey(GuestPermission, on_delete=models.CASCADE, verbose_name=_("Гостевое разрешение"))
    guest_action = models.ForeignKey(GuestAction, on_delete=models.CASCADE, verbose_name=_("Гостевое действие"))

    class Meta:
        verbose_name = "Действие разрешения"
        verbose_name_plural = "Действия разрешений"

    def __str__(self):
        return f"{self.guest_permission} -> {self.guest_action}"


class Cryptocurrency(models.Model):
    """
    Модель криптовалюты с её названием, символом, сетью и текущей ценой.
    """
    name = models.CharField(max_length=100, verbose_name=_("Название"))
    symbol = models.CharField(max_length=10, verbose_name=_("Символ"))
    network = models.CharField(max_length=50, verbose_name=_("Сеть"))
    price = models.DecimalField(max_digits=15, decimal_places=8, default=0.0, blank=True, verbose_name=_("Цена"))


    class Meta:
        verbose_name = "Криптовалюта"
        verbose_name_plural = "Криптовалюты"

    def __str__(self):
        return f"{self.name} ({self.symbol})"


class TradingPair(models.Model):
    """
    Торговая пара (base/quote), по которой пользователи могут размещать ордера.
    """
    base_currency = models.ForeignKey(Cryptocurrency, on_delete=models.CASCADE, related_name='base_pairs', verbose_name=_("Базовая валюта"))
    quote_currency = models.ForeignKey(Cryptocurrency, on_delete=models.CASCADE, related_name='quote_pairs', verbose_name=_("Котируемая валюта"))
    is_active = models.BooleanField(default=True, verbose_name=_("Активна"))

    class Meta:
        verbose_name = "Торговая пара"
        verbose_name_plural = "Торговые пары"

    def __str__(self):
        return f"{self.base_currency.symbol}/{self.quote_currency.symbol}"


class Wallet(models.Model):
    """
    Кошелёк пользователя для определённой криптовалюты, содержит баланс и дату последней транзакции.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("Пользователь"))
    crypto = models.ForeignKey(Cryptocurrency, on_delete=models.CASCADE, verbose_name=_("Криптовалюта"))
    balance = models.DecimalField(max_digits=20, decimal_places=8, verbose_name=_("Баланс"))
    last_transaction_date = models.DateTimeField(null=True, blank=True, verbose_name=_("Дата последней транзакции"))

    class Meta:
        verbose_name = "Кошелёк"
        verbose_name_plural = "Кошельки"
        ordering = ['-last_transaction_date']

    def __str__(self):
        return f"{self.user.email} — {self.crypto.symbol}"


class Order(models.Model):
    """
    Торговый ордер пользователя — на покупку или продажу криптовалюты по торговой паре.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name=_("Пользователь"))
    trading_pair = models.ForeignKey(TradingPair, on_delete=models.CASCADE, related_name='orders', verbose_name=_("Торговая пара"))

    TYPE_CHOICES = [
        ('buy', 'покупка'),
        ('sell', 'продажа'),
    ]

    type = models.CharField(max_length=10, choices=TYPE_CHOICES, verbose_name=_("Тип"))
    price = models.DecimalField(max_digits=20, decimal_places=8, verbose_name=_("Цена"))
    volume = models.DecimalField(max_digits=20, decimal_places=8, verbose_name=_("Объём"))
    
    @property
    def total_value(self):
        return self.volume * self.price
    
    STATUS_CHOICES = [
        ('pending', 'в ожидании'),
        ('partially_completed', 'частично завершено'),
        ('completed', 'завершено'),
        ('cancelled', 'отменено'),
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name=_("Статус"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Создано"))

    class Meta:
        verbose_name = "Ордер"
        verbose_name_plural = "Ордеры"
        ordering = ['-created_at']

    # Валидация ордеров
    def clean(self) -> None:
        """
        Валидация ордера на покупку или продажу:
        проверка достаточности средств в кошельке пользователя.

        Raises:
            ValidationError: При недостатке средств или отсутствии кошелька.
        """
        if self.type == 'buy':
            quote_wallet = Wallet.objects.get(user=self.user, crypto=self.trading_pair.quote_currency)
            total_cost = self.price * self.volume
        if quote_wallet.balance < total_cost:
            raise ValidationError("Недостаточно средств для покупки.")
        elif self.type == 'sell':
            base_wallet = Wallet.objects.get(user=self.user, crypto=self.trading_pair.base_currency)
        if base_wallet.balance < self.volume:
            raise ValidationError("Недостаточно средств для продажи.")

    def __str__(self):
        return f"{self.type} {self.volume} {self.trading_pair} by {self.user.email}"


class Transaction(models.Model):
    """
    Транзакция — пополнение, вывод или торговая операция, связанная с пользователем и криптовалютой.
    """
    # order и counter_order - добавлены новые
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="transactions")
    counter_order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name="counter_transactions")

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("Пользователь"))
    crypto = models.ForeignKey(Cryptocurrency, on_delete=models.CASCADE, verbose_name=_("Криптовалюта"))

    TYPE_CHOICES = [
        ('deposit', 'депозит'),
        ('withdrawal', 'вывод'),
        ('trade', 'торговля'),
    ]

    type = models.CharField(max_length=10, choices=TYPE_CHOICES, verbose_name="Тип")
    amount = models.DecimalField(max_digits=20, decimal_places=8, verbose_name=_("Сумма"))
    fee = models.DecimalField(max_digits=20, decimal_places=8, verbose_name=_("Комиссия"))
    total_amount = models.DecimalField(max_digits=20, decimal_places=8, verbose_name=_("Итоговая сумма"))

    STATUS_CHOICES = [
        ('pending', 'в ожидании'),
        ('completed', 'завершено'),
        ('cancelled', 'отменено'),
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name="Статус")
    timestamp = models.DateTimeField(default=timezone.now, verbose_name=_("Дата и время"))
    description = models.TextField(blank=True, verbose_name=_("Описание"))
    is_refunded = models.BooleanField(default=False, verbose_name=_("Возвращено"))

    class Meta:
        verbose_name = "Транзакция"
        verbose_name_plural = "Транзакции"
        ordering = ['-timestamp']

    # Валидация транзакций
    def save(self, *args, **kwargs) -> None:
        """
        Сохраняет транзакцию, предварительно проверяя баланс при выводе средств.

        Raises:
            ValidationError: Если недостаточно средств или кошелёк не найден.
        """
        if self.type == 'withdrawal':
            try:
                wallet = Wallet.objects.get(user=self.user, crypto=self.crypto)
                if self.amount > wallet.balance:
                    raise ValidationError("Недостаточно средств для вывода.")
            except Wallet.DoesNotExist:
                raise ValidationError("Кошелёк для данной криптовалюты не найден.")

        super().save(*args, **kwargs)

    def __str__(self):
        # return f"Transaction #{self.id} — {self.user.email}"
        return f"{self.type} by {self.user.email}"


class TransactionReport(models.Model):
    """
    Сгенерированный отчёт по транзакциям, загружаемый в виде файла.
    """
    file = models.FileField(upload_to='reports/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Отчёт от {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class TransactionHistory(models.Model):
    """
    История изменений конкретной транзакции (например, смена статуса).
    """
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, verbose_name=_("Транзакция"))
    amount = models.DecimalField(max_digits=20, decimal_places=8, verbose_name=_("Сумма"))
    symbol = models.CharField(max_length=10, verbose_name=_("Символ"))
    # type = models.CharField(max_length=10, verbose_name=_("Тип"))
    TYPE_CHOICES = [
        ('deposit', 'депозит'),
        ('withdrawal', 'вывод'),
        ('trade', 'торговля'),
    ]
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, verbose_name="Тип")
    # status = models.CharField(max_length=20, verbose_name=_("Статус"))
    STATUS_CHOICES = [
        ('pending', 'в ожидании'),
        ('completed', 'завершено'),
        ('cancelled', 'отменено'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name="Статус")
    changed_at = models.DateTimeField(verbose_name=_("Дата изменения"))
    description = models.TextField(blank=True, verbose_name=_("Описание"))

    class Meta:
        verbose_name = "История транзакции"
        verbose_name_plural = "Истории транзакций"
        ordering = ['-changed_at']

    def __str__(self):
        return f"История транзакции #{self.transaction.id}"


class SupportTicket(models.Model):
    """
    Заявка пользователя в техническую поддержку с темой и статусом.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("Пользователь"))
    subject = models.CharField(max_length=255, verbose_name=_("Тема"))
    # status = models.CharField(max_length=50, verbose_name=_("Статус"))
    STATUS_CHOICES = [
        ('open', 'открыто'),
        ('closed', 'закрыто'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Создано"))

    class Meta:
        verbose_name = "Тикет поддержки"
        verbose_name_plural = "Тикеты поддержки"
        ordering = ['-created_at']

    def __str__(self):
        return f"Тикет #{self.id} — {self.subject}"


class Promotion(models.Model):
    """
    Акция или промо, в которой пользователи могут участвовать, с датами, описанием и изображением.
    """
    title = models.CharField(max_length=255, verbose_name=_("Название"))
    description = models.TextField(verbose_name=_("Описание"))
    start_date = models.DateTimeField(verbose_name=_("Дата начала"))
    end_date = models.DateTimeField(verbose_name=_("Дата окончания"))
    image = models.ImageField(upload_to='promotions/', blank=True, null=True, verbose_name=_("Изображение"))
    website = models.URLField(blank=True, null=True, verbose_name=_("Веб-сайт"))

    # Добавляем ManyToMany через промежуточную модель
    users = models.ManyToManyField(
        'User',
        through='UserPromotion',
        related_name='promotions',
        verbose_name=_("Участники")
    )

    class Meta:
        verbose_name = "Акция"
        verbose_name_plural = "Акции"
        ordering = ['-start_date']

    def get_absolute_url(self) -> str:
        """
        Возвращает абсолютный URL для детального просмотра акции.

        Returns:
            str: URL-адрес, ведущий на страницу акции.
        """
        return reverse("promotion_detail", args=[self.id])


    @property
    def is_active(self) -> bool:
        """
        Проверяет, активна ли акция в текущий момент времени.

        Returns:
            bool: True, если текущая дата находится между датами начала и окончания акции.
        """
        now = timezone.now()
        return self.start_date <= now <= self.end_date
    
    def __str__(self):
        return self.title

class UserPromotion(models.Model):
    """
    Связь между пользователем и акцией, фиксирующая факт участия и его статус.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("Пользователь"))
    promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE, verbose_name=_("Акция"))
    participation_date = models.DateTimeField(verbose_name=_("Дата участия"))

    STATUS_CHOICES = [
        ('active', 'Активен'),
        ('completed', 'Завершил'),
        ('cancelled', 'Отменил участие')
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name=_("Статус"), default='active')

    class Meta:
        verbose_name = "Участие в акции"
        verbose_name_plural = "Участия в акциях"
        unique_together = ('user', 'promotion')
        ordering = ['-participation_date']

    def __str__(self):
        return f"{self.user.email} — {self.promotion.title}"


class brexam(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название экзамена")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания записи")
    exam_date = models.DateField(verbose_name="Дата проведения экзамена")
    image = models.ImageField(upload_to='exam_images/', verbose_name="Изображение задания")
    participants = models.ManyToManyField(User, verbose_name="Участники экзамена")
    is_public = models.BooleanField(default=False, verbose_name="Опубликовано")