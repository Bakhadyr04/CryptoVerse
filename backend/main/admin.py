from django.contrib import admin

from main.forms import CryptocurrencyAdminForm

# from main.forms import CryptocurrencyAdminForm
from .models import *
from .models import UserPromotion, Transaction
from django.utils.html import format_html
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from django.core.files.base import ContentFile
from main.models import TransactionReport  
from io import BytesIO
import os


class UserAdmin(admin.ModelAdmin):
    """
    Админ-интерфейс для модели пользователя.
    """
    list_display = ("id", "email", "name", "role", "created_at")
    search_fields = ("email", "name")
    list_filter = ("role", "created_at")
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "last_login")
    exclude = ['groups', 'user_permissions', 'is_superuser']

    def has_add_permission(self, request) -> bool:
        """Отключает возможность добавления пользователей через админку."""
        return True

    def has_change_permission(self, request, obj=None) -> bool:
        """Отключает возможность редактирования пользователей."""
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        """Разрешает удаление пользователей."""
        return True

    def has_view_permission(self, request, obj=None) -> bool:
        """Разрешает просмотр пользователей."""
        return True
    

class WalletAdmin(admin.ModelAdmin):
    """
    Отображает кошельки пользователей.
    """
    list_display = ("user", "balance", "crypto", "last_transaction_date")
    raw_id_fields = ("user", "crypto")
    search_fields = ("user__email", "crypto__symbol")
    list_filter = ("crypto", "last_transaction_date")
    date_hierarchy = "last_transaction_date"

    def has_add_permission(self, request) -> bool:
        """Отключает добавление кошельков."""
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        """Отключает редактирование кошельков."""
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        """Отключает удаление кошельков."""
        return False

    def has_view_permission(self, request, obj=None) -> bool:
        """Разрешает просмотр кошельков."""
        return True


class OrderAdmin(admin.ModelAdmin):
    """
    Админ-панель для просмотра ордеров пользователей.
    """
    @admin.display(description="Объём * Цена")
    def total_value(self, obj) -> float:
        """
        Вычисляет итоговую стоимость ордера.

        Args:
            obj: Экземпляр модели Order.

        Returns:
            float: Общая стоимость (volume * price).
        """
        return obj.volume * obj.price

    list_display = ("user", "trading_pair", "type", "price", "volume", "status", "created_at")
    raw_id_fields = ("user", "trading_pair")
    search_fields = ("user__email", "trading_pair__base_currency__symbol")
    list_filter = ("type", "status", "trading_pair", "created_at")
    readonly_fields = ('total_value', "status")
    date_hierarchy = "created_at"

    def has_add_permission(self, request) -> bool:
        """Отключает возможность добавления ордеров."""
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        """Отключает возможность редактирования ордеров."""
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        """Отключает возможность удаления ордеров."""
        return False

    def has_view_permission(self, request, obj=None) -> bool:
        """Разрешает просмотр ордеров."""
        return True


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """
    Просмотр транзакций и экспорт в PDF.
    """
    list_display = ("user", "crypto", "type", "total_amount", "status", "timestamp", "is_refunded")
    # "amount", "fee",
    raw_id_fields = ("user", "crypto")
    search_fields = ("user__email", "crypto__symbol")
    list_filter = ("type", "status", "is_refunded", "timestamp", "crypto")
    date_hierarchy = "timestamp"

    def has_add_permission(self, request) -> bool:
        """Отключает возможность добавления транзакций."""
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        """Отключает возможность редактирования транзакций."""
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        """Отключает возможность удаления транзакций."""
        return False

    def has_view_permission(self, request, obj=None) -> bool:
        """Разрешает просмотр транзакций."""
        return True


    # Экспорт транзакций в PDF
    actions = ["export_transactions_pdf"]
    
    @admin.action(description="Экспорт выбранных транзакций в PDF")
    def export_transactions_pdf(self, request, queryset) -> HttpResponse:
        """
        Генерирует и экспортирует PDF-файл со списком выбранных транзакций.

        Args:
            request: Объект запроса администратора.
            queryset: Выбранные объекты Transaction.

        Returns:
            HttpResponse с PDF-файлом.
        """
        font_path = os.path.join('main/static/fonts/DejaVuSans.ttf')
        pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)

        data = []
        data.append(["Пользователь", "Крипто", "Тип", "Сумма", "Статус", "Дата"])

        for tx in queryset:
            data.append([
                tx.user.email,
                tx.crypto.symbol,
                tx.type,
                f"{tx.amount:.2f}",
                tx.status,
                tx.timestamp.strftime('%Y-%m-%d %H:%M'),
            ])

        table = Table(data, repeatRows=1)
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (3, 1), (3, -1), 'RIGHT'),
        ])
        table.setStyle(style)

        title_style = ParagraphStyle(
        name='Title',
        fontName='DejaVuSans',
        fontSize=18,
        alignment=TA_CENTER,
        spaceAfter=20,
        )
        title = Paragraph("Отчёт по Транзакциям", title_style)

        elements = [title, Spacer(1, 12), table]
        doc.build(elements)

        buffer.seek(0)
        
        pdf_file = ContentFile(buffer.getvalue())
        report = TransactionReport()
        report.file.save("transactions.pdf", pdf_file)
        report.save()

        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="transactions.pdf"'
        return response

    export_transactions_pdf.short_description = "Экспорт выбранных транзакций в PDF"
    

class TransactionHistoryAdmin(admin.ModelAdmin):
    """
    Просмотр истории изменений транзакций.
    """
    list_display = ("transaction", "amount", "symbol", "type", "status", "changed_at")
    raw_id_fields = ("transaction",)
    search_fields = ("transaction__id", "symbol", "transaction__user__email", "transaction__user__name")
    list_filter = ("status", "type", "changed_at", "symbol")
    date_hierarchy = "changed_at"

    def has_add_permission(self, request) -> bool:
        """Отключает возможность добавления истории транзакций."""
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        """Отключает возможность редактирования истории."""
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        """Отключает возможность удаления истории."""
        return False

    def has_view_permission(self, request, obj=None) -> bool:
        """Разрешает просмотр истории транзакций."""
        return True


class SupportTicketAdmin(admin.ModelAdmin):
    """
    Просмотр тикетов поддержки от пользователей.
    """
    list_display = ("user", "subject", "status", "created_at")
    raw_id_fields = ("user",)
    search_fields = ("subject", "user__email")
    list_filter = ("status", "created_at")
    date_hierarchy = "created_at"

    def has_add_permission(self, request) -> bool:
        """Отключает возможность добавления тикетов."""
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        """Отключает возможность редактирования тикетов."""
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        """Отключает возможность удаления тикетов."""
        return False

    def has_view_permission(self, request, obj=None) -> bool:
        """Разрешает просмотр тикетов."""
        return True


class UserPromotionInline(admin.TabularInline):
    """
    Просмотр участий пользователей в акциях.
    """
    model = UserPromotion
    can_delete = False
    extra = 0
    readonly_fields = ['user', 'participation_date']

    def has_add_permission(self, request) -> bool:
        """Отключает возможность добавления участий."""
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        """Отключает возможность редактирования участий."""
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        """Отключает возможность удаления участий."""
        return False

    def has_view_permission(self, request, obj=None) -> bool:
        """Разрешает просмотр участий."""
        return True


class PromotionAdmin(admin.ModelAdmin):
    """
    Просмотр и редактирование акций.
    """
    list_display = ("title", "image_preview", "start_date", "end_date")
    list_filter = ("start_date", "end_date")
    # inlines = [UserPromotionInline]
    date_hierarchy = "start_date"
    search_fields = ("title",)
    readonly_fields = ['image_preview']

    fieldsets = (
        (None, {
            'fields': ("title", "description", "image", "start_date", "end_date")
        }),
    )

    def has_add_permission(self, request) -> bool:
        """Разрешает добавления акций."""
        return True

    def has_change_permission(self, request, obj=None) -> bool:
        """Разрешает возможность редактирования акций."""
        return True

    def has_delete_permission(self, request, obj=None) -> bool:
        """Разрешает удаление акций."""
        return True

    def has_view_permission(self, request, obj=None) -> bool:
        """Разрешает просмотр акций."""
        return True


    def get_readonly_fields(self, request, obj=None) -> list[str]:
        """
        Возвращает список полей, доступных только для чтения в админке.

        Args:
            request: Текущий объект запроса администратора.
            obj: Объект модели, если он уже существует (редактирование),
                 или None при создании нового объекта.

        Returns:
            Список полей, которые должны быть только для чтения.
            Если объект уже существует — поля start_date и end_date становятся недоступными для редактирования.
        """
        if obj:  # редактирование существующего
            return ["start_date", "end_date"]
        return []  # при создании — всё доступно
    
    @admin.display(description="Превью")
    def image_preview(self, obj) -> str:
        """
        Отображает миниатюру изображения акции.

        Args:
            obj: Экземпляр модели Promotion.

        Returns:
            HTML-разметка изображения или текст, если изображения нет.
        """
        if obj.image:
            return format_html('<img src="{}" width="50" />', obj.image.url)
        return "Нет изображения"
    image_preview.short_description = "Превью"


class GuestPermissionActionInline(admin.TabularInline):
    """
    Инлайн-форма для отображения действий, связанных с гостевыми разрешениями.

    Используется в интерфейсе администратора для редактирования модели
    GuestPermission и её связи с GuestAction через промежуточную модель.
    """
    model = GuestPermissionsActions
    raw_id_fields = ("guest_action",)
    extra = 0


class GuestPermissionAdmin(admin.ModelAdmin):
    """
    Настройка разрешений для гостей (видимость, вход, регистрация).
    """
    list_display = ("page_name", "can_view", "can_register", "can_login", "created_at")
    inlines = [GuestPermissionActionInline]
    date_hierarchy = "created_at"
    list_filter = ("can_view", "can_register", "can_login", "created_at")

    def has_add_permission(self, request) -> bool:
        """Разрешает добавление разрешений."""
        return True

    def has_change_permission(self, request, obj=None) -> bool:
        """Разрешает редактирование разрешений."""
        return True

    def has_delete_permission(self, request, obj=None) -> bool:
        """Разрешает удаление разрешений."""
        return True

    def has_view_permission(self, request, obj=None) -> bool:
        """Разрешает просмотр разрешений."""
        return True


class GuestActionAdmin(admin.ModelAdmin):
    """
    Просмотр действий, доступных гостям (вход, регистрация).
    """
    list_display = ("action_name", "can_execute", "created_at")
    search_fields = ("action_name",)
    list_filter = ("can_execute", "created_at")
    date_hierarchy = "created_at"

    def has_add_permission(self, request) -> bool:
        """Разрешает добавление действий."""
        return True

    def has_change_permission(self, request, obj=None) -> bool:
        """Разрешает редактирование действий."""
        return True

    def has_delete_permission(self, request, obj=None) -> bool:
        """Разрешает удаление действий."""
        return True

    def has_view_permission(self, request, obj=None) -> bool:
        """Разрешает просмотр действий."""
        return True


class GuestPermissionsActionsAdmin(admin.ModelAdmin):
    """
    Промежуточная таблица: какие действия разрешены для каких страниц.
    """
    list_display = ("guest_permission", "guest_action")
    raw_id_fields = ("guest_permission", "guest_action")


class CryptocurrencyAdmin(admin.ModelAdmin):
    """
    Просмотр криптовалют (имя, символ, сеть, цена).
    """
    form = CryptocurrencyAdminForm
    list_display = ("name", "symbol", "network", "formatted_price")
    list_filter = ("network",)
    search_fields = ("name", "symbol")
    fields = ("name", "symbol", "network", "price")
    readonly_fields = ("formatted_price",)

    @admin.display(description="Цена ($)", ordering="price")
    def formatted_price(self, obj) -> str:
        """
        Форматирует цену криптовалюты с двумя знаками после запятой и знаком $.
        """
        return f"${obj.price:.2f}"
    formatted_price.short_description = "Цена ($)"
    formatted_price.admin_order_field = "price"
    
    def has_add_permission(self, request):
        return True  # разрешить добавление

    def has_change_permission(self, request, obj=None):
        return True  # разрешить редактирование

    def has_delete_permission(self, request, obj=None):
        return True  # если надо разрешить удаление

    def has_view_permission(self, request, obj=None):
        return True


class TradingPairAdmin(admin.ModelAdmin):
    """
    Просмотр торговых пар (BTC/USDT, ETH/USD).
    """
    list_display = ("base_currency", "quote_currency", "is_active")
    raw_id_fields = ("base_currency", "quote_currency")
    list_filter = ("is_active",)


class UserPromotionAdmin(admin.ModelAdmin):
    list_display = ("user", "promotion", "participation_date")
    raw_id_fields = ("user", "promotion")
    date_hierarchy = "participation_date"
    search_fields = ("user__email", "promotion__title")
    list_filter = ("participation_date", "promotion")

    def has_add_permission(self, request):
        return False  # запрет на добавление

    def has_change_permission(self, request, obj=None):
        return False  # запрет на изменение

    def has_delete_permission(self, request, obj=None):
        return False  # запрет на удаление

    def has_view_permission(self, request, obj=None):
        return True  # разрешение только на просмотр


# class GuestSessionAdmin(admin.ModelAdmin):
#     list_display = ("user", "ip_address", "last_activity", "created_at")
#     raw_id_fields = ("user",)
#     search_fields = ("user__email", "ip_address")
#     date_hierarchy = "created_at"
#     list_filter = ("last_activity",)

class GuestSessionAdmin(admin.ModelAdmin):
    """
    Просмотр гостевых сессий (IP, токен, активность).
    """
    list_display = ['id', 'ip_address', 'last_activity', 'created_at']
    readonly_fields = ['session_token', 'ip_address', 'last_activity', 'created_at']
    list_filter = ("last_activity", "created_at")

    def has_add_permission(self, request) -> bool:
        """Отключает возможность добавления сессий."""
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        """Отключает возможность редактирования сессий."""
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        """Отключает возможность удаления сессий."""
        return False

    def has_view_permission(self, request, obj=None) -> bool:
        """Разрешает просмотр сессий."""
        return True

class PageAdmin(admin.ModelAdmin):
    """
    Управление страницами, доступными в системе.
    """
    list_display = ("page_name", "can_view", "created_at")
    search_fields = ("page_name",)
    list_filter = ("can_view", "created_at")
    date_hierarchy = "created_at"


admin.site.register(User, UserAdmin)
admin.site.register(Wallet, WalletAdmin)
admin.site.register(Order, OrderAdmin)
# admin.site.register(Transaction, TransactionAdmin)
admin.site.register(TransactionHistory, TransactionHistoryAdmin)
admin.site.register(SupportTicket, SupportTicketAdmin)
admin.site.register(Promotion, PromotionAdmin)
admin.site.register(GuestPermission, GuestPermissionAdmin)
admin.site.register(GuestAction, GuestActionAdmin)
admin.site.register(GuestPermissionsActions, GuestPermissionsActionsAdmin)
admin.site.register(Cryptocurrency, CryptocurrencyAdmin)
admin.site.register(TradingPair, TradingPairAdmin)
admin.site.register(UserPromotion, UserPromotionAdmin)
admin.site.register(GuestSession, GuestSessionAdmin)
admin.site.register(Page, PageAdmin)