from django.core.management.base import BaseCommand
from main.models import *
from main.models import UserPromotion

class Command(BaseCommand):
    help = "Удаление всех фейковых данных, кроме пользователей с ролью 'admin'"

    def handle(self, *args, **kwargs):
        self.stdout.write("\nУдаление фейковых данных...")

        GuestPermissionsActions.objects.all().delete()
        GuestPermission.objects.all().delete()
        GuestAction.objects.all().delete()
        GuestSession.objects.all().delete()
        Page.objects.all().delete()

        UserPromotion.objects.all().delete()
        Promotion.objects.all().delete()
        SupportTicket.objects.all().delete()
        TransactionHistory.objects.all().delete()
        Transaction.objects.all().delete()
        Order.objects.all().delete()
        Wallet.objects.all().delete()
        TradingPair.objects.all().delete()
        Cryptocurrency.objects.all().delete()

        User.objects.filter(is_superuser=False).delete()

        self.stdout.write(self.style.SUCCESS("\nВсе фейковые данные успешно удалены."))