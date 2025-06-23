from django.contrib.auth import authenticate, login, get_user_model
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from main.forms import CustomUserCreationForm
from main.models import Cryptocurrency, User, UserPromotion, brexam
from django.shortcuts import render, redirect, get_object_or_404    
from django.db.models import Sum, Count, Q, Avg
from main.models import GuestSession, Order, Promotion, Transaction, User
from silk.profiling.profiler import silk_profile
from django.core.paginator import Paginator
import json


def index(request: HttpRequest) -> HttpResponse:
    """
    Отображает главную страницу приложения.

    Args:
        request: HTTP-запрос от клиента.

    Returns:
        HTML-страница index.html.
    """
    return render(request, "index.html")

# Обновление времени последнего входа пользователя
@csrf_exempt  # только если нет CSRF-токена (например, в Postman)
def login_view(request: HttpRequest) -> JsonResponse:
    """
    Авторизация пользователя по email и паролю.

    Args:
        request: HTTP POST-запрос с JSON-данными {"email": ..., "password": ...}.

    Returns:
        JSON-ответ с сообщением об успехе или ошибке.
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')

        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)  # обновляется last_login автоматически
            return JsonResponse({'message': 'Вход выполнен успешно'})
        else:
            return JsonResponse({'error': 'Неверный email или пароль'}, status=401)

    return JsonResponse({'error': 'Допустим только POST-запрос'}, status=405)


# Использование related_name для транзакции
@require_GET
def order_transactions_view(request: HttpRequest, order_id: int) -> JsonResponse:
    """
    Возвращает прямые и обратные транзакции для указанного заказа.

    Args:
        request: Объект запроса.
        order_id: ID заказа.

    Returns:
        JSON с прямыми и обратными транзакциями.
    """
    order = get_object_or_404(Order, id=order_id)

    direct = order.transactions.values("id", "amount", "type", "timestamp")
    counter = order.counter_transactions.values("id", "amount", "type", "timestamp")

    return JsonResponse({
        "order_id": order_id,
        "direct_transactions": list(direct),
        "counter_transactions": list(counter)
    })


# Проверка активности акции - http://localhost:8000/participate/3/
def participate(request: HttpRequest, promo_id: int) -> JsonResponse:
    """
    Проверка возможности участия в акции.

    Args:
        request: Объект запроса.
        promo_id: ID акции.

    Returns:
        JSON с сообщением или ошибкой, если акция завершена.
    """
    promo = get_object_or_404(Promotion, id=promo_id)

    if not promo.is_active:
        return JsonResponse({'error': 'Акция уже завершена'}, status=400)

    return JsonResponse({'message': 'Участие в акции успешно зарегистрировано'})


# Удаление неактивных гостевых сессий - командой python manage.py delete_old_guests
class Command(BaseCommand): 
    """
    Django management-команда для удаления просроченных гостевых сессий.
    """
    help = 'Удаляет гостевые сессии, неактивные более 24 часов'

    def handle(self, *args, **kwargs) -> None:
        """
        Основной метод, вызываемый при выполнении команды.
        """
        cutoff = timezone.now() - timedelta(days=1)
        old_sessions = GuestSession.objects.filter(last_activity__lt=cutoff)
        count = old_sessions.count()
        old_sessions.delete()

        self.stdout.write(self.style.SUCCESS(f"Удалено {count} просроченных гостевых сессий"))


# Исключаем администраторов - http://localhost:8000/non-admin-users/
@require_GET
def non_admin_users(request: HttpRequest) -> JsonResponse:
    """
    Получает список пользователей, не являющихся администраторами.

    Args:
        request: Объект запроса.

    Returns:
        JSON со списком пользователей без роли 'admin'.
    """
    users = User.objects.exclude(role="admin")
    data = [
        {
            "id": user.id,
            "email": user.email,
            "role": user.role,
        } for user in users
    ]
    return JsonResponse({"non_admin_users": data})


# Сортировка транзакций по дате и времени - http://localhost:8000/recent-transactions/
# @silk_profile(name='recent_transactions')
def recent_transactions(request: HttpRequest) -> JsonResponse:
    """
    Получает последние 20 транзакций по убыванию времени.

    Args:
        request: Объект запроса.

    Returns:
        JSON с последними транзакциями.
    """
    transactions = Transaction.objects.all().order_by("-timestamp")[:20]

    data = [
        {
            "id": t.id,
            "type": t.type,
            "amount": float(t.amount),
            "status": t.status,
            "timestamp": t.timestamp,
        } for t in transactions
    ]

    return JsonResponse({"recent_transactions": data})


# Пользователи, активные за последние 24 часа
@require_GET
def active_users_last_24h(request: HttpRequest) -> JsonResponse:
    """
    Получает пользователей, активных за последние 24 часа.

    Args:
        request: Объект запроса.

    Returns:
        JSON со списком активных пользователей.
    """
    users = User.objects.active_last_24h()
    data = [
        {
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "last_login": user.last_login,
        } for user in users
    ]
    return JsonResponse({"active_last_24h": data})


class PromotionDetailView(DetailView):
    model = Promotion
    template_name = "promotion_detail.html"

# Находит объект (акцию) по id и передает в шаблон
@require_GET
def promotion_detail_link(request: HttpRequest, promo_id: int) -> JsonResponse:
    """
    Получает ссылку на детальную страницу акции по её ID.

    Args:
        request: Объект запроса.
        promo_id: ID акции.

    Returns:
        JSON со ссылкой или ошибкой, если акция не найдена.
    """
    try:
        promo = Promotion.objects.get(id=promo_id)
        url = promo.get_absolute_url()
        return JsonResponse({"url": url})
    except Promotion.DoesNotExist:
        return JsonResponse({"error": "Акция не найдена"}, status=404)





# Общая сумма всех транзакций (aggregate) - http://localhost:8000/total-transaction-amount/
@require_GET 
def total_transaction_amount(request: HttpRequest) -> JsonResponse:
    """
    Возвращает сумму всех транзакций в системе.

    Args:
        request: Объект запроса.

    Returns:
        JSON с общей суммой.
    """
    total = Transaction.objects.aggregate(total_amount=Sum("amount"))
    return JsonResponse(total)

# Сумма транзакций по каждому пользователю (annotate) - http://localhost:8000/user-transaction-sums/
@require_GET
# @silk_profile(name='user_transaction_sums')
def user_transaction_sums(request: HttpRequest) -> JsonResponse:
    """
    Получает сумму транзакций по каждому пользователю.

    Args:
        request: Объект запроса.

    Returns:
        JSON со списком пользователей и суммой их транзакций.
    """
    users = User.objects.annotate(total_amount=Sum("transaction__amount"))
    data = [
        {
            "id": user.id,
            "email": user.email,
            "total_amount": float(user.total_amount or 0),
        } for user in users
    ]
    return JsonResponse({"users": data})

# Кол-во акций в которых участвует пользователь (annotate) - http://localhost:8000/user-promotion-counts/
@require_GET
def user_promotion_counts(request: HttpRequest) -> JsonResponse:
    """
    Возвращает количество акций, в которых участвует каждый пользователь.

    Args:
        request: Объект запроса.

    Returns:
        JSON со списком пользователей и количеством их участий в акциях.
    """
    users = User.objects.annotate(promo_count=Count("userpromotion"))
    data = [
        {
            "id": user.id,
            "email": user.email,
            "promo_count": user.promo_count,
        } for user in users
    ]
    return JsonResponse({"users": data})

def promotions_list(request: HttpRequest) -> HttpResponse:
    """
    Отображает список всех акций.

    Args:
        request: Объект запроса.

    Returns:
        HTML-страница со всеми акциями.
    """
    promotions = Promotion.objects.all()
    return render(request, 'promotions_list.html', {'promotions': promotions})



# Редирект на Акции - http://localhost:8000/promotions/
@require_POST
def add_promotion(request: HttpRequest) -> HttpResponse | JsonResponse:
    """
    Добавляет новую акцию. Ожидается POST-запрос с title и description.

    Args:
        request: Объект запроса.

    Returns:
        Редирект на список акций или сообщение об ошибке.
    """
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")

        if not title:
            return JsonResponse({"error": "Title is required"}, status=400)

        now = timezone.now()

        Promotion.objects.create(
            title=title,
            description=description,
            start_date=now,
            end_date=now + timezone.timedelta(days=7)
        )

        return redirect('/promotions/')  # редирект на список акций

    # Если GET запрос — можно вернуть форму или 404
    return JsonResponse({"error": "Invalid request method"}, status=405)

def delete_promotion(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Удаляет акцию по её первичному ключу.

    Args:
        request: Объект запроса.
        pk: ID акции.

    Returns:
        Редирект на список акций.
    """
    promo = get_object_or_404(Promotion, pk=pk)
    promo.delete()
    return redirect('promotions_list')

def edit_promotion(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Позволяет отредактировать акцию по её ID.

    Args:
        request: Объект запроса.
        pk: ID акции.

    Returns:
        Отрендеренная форма редактирования или редирект на список акций.
    """
    promo = get_object_or_404(Promotion, pk=pk)

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")

        if not title:
            return render(request, "promotion_edit.html", {
                "promo": promo,
                "error": "Название обязательно",
            })

        promo.title = title
        promo.description = description
        promo.save()

        return redirect('promotions_list')  # Редирект на список после успешного редактирования

    return render(request, "promotion_edit.html", {"promo": promo})

def promotion_detail_redirect(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Отображает детальную страницу акции или редиректит на список, если акция не найдена.

    Args:
        request: Объект запроса.
        pk: ID акции.

    Returns:
        HTML-страница с детальной информацией или редирект.
    """
    try:
        promo = Promotion.objects.get(pk=pk)
    except Promotion.DoesNotExist:
        return redirect('promotions_list')
    return render(request, 'promotion_detail.html', {'promo': promo})



# Фильтрация акций по ключевому слову — http://localhost:8000/promotions/search/?q=бонус
@require_GET
def search_promotions(request: HttpRequest) -> HttpResponse:
    """
    Фильтрует акции по ключевому слову в заголовке или описании.

    Args:
        request: Объект запроса с параметром `q`.

    Returns:
        HTML-страница со списком отфильтрованных акций.
    """
    query = request.GET.get('q', '')
    
    # Сравнение без учёта регистра
    promotions = Promotion.objects.filter(
        Q(title__icontains=query) | Q(description__icontains=query)
    )

    return render(request, 'promotions_list.html', {'promotions': promotions})



# Получаем список акций как словари - http://localhost:8000/promotions/values/
@require_GET
def promotion_titles_values(request: HttpRequest) -> JsonResponse:
    """
    Возвращает список акций в виде кортежей (id, title, description, start_date, end_date).

    Args:
        request: Объект запроса.

    Returns:
        JSON с кортежами акций.
    """
    data = Promotion.objects.values_list("id", "title", "description", "start_date", "end_date")
    
    return JsonResponse({"promotions": list(data)})


# Получаем транзакции пользователей, участвующих в активных акциях - http://localhost:8000/transactions/by-active-promotions/
@require_GET 
def transactions_by_active_promotions(request: HttpRequest) -> JsonResponse:
    """
    Получает транзакции от пользователей, участвующих в активных акциях.

    Args:
        request: Объект запроса.
    
    Returns:
        JSON с транзакциями.
    """
    active_ids = Promotion.objects.filter(end_date__gte=timezone.now()).values_list("id", flat=True)
    user_ids = UserPromotion.objects.filter(promotion_id__in=active_ids).values_list("user_id", flat=True)
    transactions = Transaction.objects.filter(user_id__in=user_ids).values("id", "user_id", "type", "amount", "status")

    return JsonResponse({"transactions": list(transactions)})

# Разобраться с flat=True, привести пример связки с методом __in


# Подсчитываем кол-во активных акций с count() и проверяем наличие ключевого слова в описании с exists() - http://localhost:8000/promotions/stats/
@require_GET
def promotion_stats(request: HttpRequest) -> JsonResponse:
    """
    Возвращает статистику по активным акциям и наличию ключевого слова "бонус" в описании.

    Args:
        request: Объект запроса.

    Returns:
        JSON с количеством активных акций и наличием ключевого слова.
    """
    total = Promotion.objects.filter(end_date__gte=timezone.now()).count()
    has_bonus = Promotion.objects.filter(description__icontains="бонус").exists()

    return JsonResponse({
        "active_promotions_count": total,
        "contains_bonus_description": has_bonus
    })


# CSRF - стандартная защита Django от подделки межсайтовых запросов, когда отправляем запрос вне браузера
# @csrf_exempt 
# Обновление описания акций по ключевому слову - http://localhost:8000/promotions/bulk-update/
@require_POST
def bulk_update_promotions(request: HttpRequest) -> JsonResponse:
    """
    Обновляет описание акций, содержащих слово "тест".

    Args:
        request: Объект запроса.

    Returns:
        JSON с количеством обновлённых записей.
    """
    updated_count = Promotion.objects.filter(description__icontains="тест").update(description="Обновлено автоматически")
    return JsonResponse({"updated_promotions": updated_count})


# @csrf_exempt
# Удаление акций, срок которых истек 30 дней назад - http://localhost:8000/promotions/bulk-delete/
@require_POST
def bulk_delete_old_promotions(request: HttpRequest) -> JsonResponse:
    """
    Удаляет акции, завершившиеся более 30 дней назад.

    Args:
        request: Объект запроса.

    Returns:
        JSON с количеством удалённых записей.
    """
    one_month_ago = timezone.now() - timedelta(days=30)
    deleted, _ = Promotion.objects.filter(end_date__lt=one_month_ago).delete()
    # deleted, _ = Promotion.objects.filter(end_date__lt=timezone.now()).delete() - удаление истекших акций в нынешнее время
    return JsonResponse({"deleted_promotions": deleted})


# представление для регистрации
class UserRegisterView(CreateView):
    """
    Представление для регистрации новых пользователей через форму.
    """
    model = User
    template_name = "registration/register.html"
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("order-list")

    def form_valid(self, form):
        """
        Обработка валидной формы регистрации.

        Args:
            form: Форма создания пользователя.

        Returns:
            HTTP-ответ с редиректом.
        """
        return super().form_valid(form)
    

# API с QuerySet для криптовалют (фильтры)
def cryptocurrency_api(request):
    queryset = Cryptocurrency.objects.all()

    search = request.GET.get('search')
    max_price = request.GET.get('max_price')
    sort = request.GET.get('sort', 'desc')

    if search:
        queryset = queryset.filter(name__icontains=search)

    if max_price:
        try:
            max_price_value = float(max_price)
            queryset = queryset.filter(price__lte=max_price_value)
        except ValueError:
            pass

    if sort == 'asc':
        queryset = queryset.order_by('price')
    else:
        queryset = queryset.order_by('-price')

    avg_price = queryset.aggregate(avg_price=Avg('price'))['avg_price']

    data = {
        'cryptocurrencies': [
            {
                'id': crypto.id,
                'name': crypto.name,
                'symbol': crypto.symbol,
                'network': crypto.network,
                'price': float(crypto.price),
            }
            for crypto in queryset
        ],
        'avg_price': round(avg_price, 2) if avg_price is not None else None
    }

    return JsonResponse(data)


# API для акций
def promotions_api(request):
    queryset = Promotion.objects.all().order_by('id')
    paginator = Paginator(queryset, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    data = {
        'promotions': [
            {
                'id': p.id,
                'title': p.title,
                'description': p.description,
                'image': p.image.url if p.image else None, 
                'start_date': p.start_date.strftime('%Y-%m-%d'),
                'end_date': p.end_date.strftime('%Y-%m-%d') if p.end_date else None,
            }
            for p in page_obj
        ],
        'total_pages': paginator.num_pages
    }

    return JsonResponse(data)



# API для пользователей
def recent_users_api(request):
    User = get_user_model()
    users = User.objects.order_by('-created_at')[:10]

    emails = []
    for user in users:
        email = getattr(user, 'email', None)
        if email:
            emails.append(email)

    return JsonResponse({'emails': emails})



# API для криптовалют к детальной странице
@csrf_exempt
def cryptocurrency_add(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        crypto = Cryptocurrency.objects.create(
            name=data.get('name'),
            symbol=data.get('symbol'),
            network=data.get('network'),
            price=data.get('price')
        )
        return JsonResponse({'status': 'success', 'id': crypto.id})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def cryptocurrency_update(request, pk):
    if request.method == 'PUT':
        try:
            crypto = Cryptocurrency.objects.get(pk=pk)
            data = json.loads(request.body)
            crypto.name = data.get('name')
            crypto.symbol = data.get('symbol')
            crypto.network = data.get('network')
            crypto.price = data.get('price')
            crypto.save()
            return JsonResponse({'status': 'success'})
        except Cryptocurrency.DoesNotExist:
            return JsonResponse({'error': 'Not found'}, status=404)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def cryptocurrency_delete(request, pk):
    if request.method == 'DELETE':
        try:
            crypto = Cryptocurrency.objects.get(pk=pk)
            crypto.delete()
            return JsonResponse({'status': 'success'})
        except Cryptocurrency.DoesNotExist:
            return JsonResponse({'error': 'Not found'}, status=404)
    return JsonResponse({'error': 'Invalid request'}, status=400)

def cryptocurrency_detail(request, pk):
    try:
        crypto = Cryptocurrency.objects.get(pk=pk)
        data = {
            'id': crypto.id,
            'name': crypto.name,
            'symbol': crypto.symbol,
            'network': crypto.network,
            'price': crypto.price,
        }
        return JsonResponse(data)
    except Cryptocurrency.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)
    



def brexam_list(request):
    exams = brexam.objects.filter(is_public=True)
    return render(request, 'brexam_list.html', {'exams': exams})