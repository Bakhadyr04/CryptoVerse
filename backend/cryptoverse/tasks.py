from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.apps import apps


@shared_task
# Удаление гостевых сессий старше 24 часов
def delete_old_guest_sessions():
    from main.models import GuestSession
    cutoff = timezone.now() - timedelta(hours=24)
    deleted_count, _ = GuestSession.objects.filter(last_activity__lt=cutoff).delete()
    return f"Удалено {deleted_count} гостевых сессий"

@shared_task
# Удаление ордеров со статусом 'pending', которым больше 24 часов
def delete_pending_orders():
    from main.models import Order
    cutoff = timezone.now() - timedelta(hours=24)
    deleted_count, _ = Order.objects.filter(status='pending', created_at__lt=cutoff).delete()
    return f"Удалено {deleted_count} ордеров в ожидании"

@shared_task
def send_daily_notifications():
    print("Ещё один прекрасный день для торговли криптой!")
    return "Ежедневные сообщения отправлены"

def setup_periodic_tasks():
    if not apps.ready:
        return

def setup_periodic_tasks():
    if not apps.ready:
        return  # Предотвращаем вызов слишком рано во время миграций

    from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule

    # Задача 1: каждый час
    hourly_schedule, _ = IntervalSchedule.objects.get_or_create(
        every=1,
        period=IntervalSchedule.HOURS
    )
    PeriodicTask.objects.get_or_create(
        interval=hourly_schedule,
        name='Удаление старых гостевых сессий',
        task='cryptoverse.tasks.delete_old_guest_sessions'
    )

    # Задача 2: каждую минуту
    minutely_schedule, _ = IntervalSchedule.objects.get_or_create(
        every=1,
        period=IntervalSchedule.MINUTES
    )
    PeriodicTask.objects.get_or_create(
        interval=minutely_schedule,
        name='Удаление ордеров в ожидании старше 24 часов',
        task='cryptoverse.tasks.delete_pending_orders'
    )

    # Задача 3: ежедневно в полночь
    daily_schedule, _ = CrontabSchedule.objects.get_or_create(
        minute='0',
        hour='0'
    )
    PeriodicTask.objects.get_or_create(
        crontab=daily_schedule,
        name='Отправка ежедневных уведомлений',
        task='cryptoverse.tasks.send_daily_notifications'
    )
