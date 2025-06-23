import uuid
from django.utils import timezone
from main.models import GuestSession

class GuestSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            session_token = request.session.get("guest_token")

            if session_token:
                try:
                    session = GuestSession.objects.get(session_token=session_token)

                    # если сессия есть — обновляем время последней активности
                    session.last_activity = timezone.now()
                    session.save(update_fields=["last_activity"])

                except GuestSession.DoesNotExist:
                    # сессия не найдена — создаём новую
                    session_token = str(uuid.uuid4())
                    request.session["guest_token"] = session_token

                    GuestSession.objects.create(
                        session_token=session_token,
                        ip_address=request.META.get("REMOTE_ADDR"),
                        last_activity=timezone.now()
                    )

            else:
                # у пользователя вообще нет токена — создаём новую сессию
                session_token = str(uuid.uuid4())
                request.session["guest_token"] = session_token

                GuestSession.objects.create(
                    session_token=session_token,
                    ip_address=request.META.get("REMOTE_ADDR"),
                    last_activity=timezone.now()
                )

        response = self.get_response(request)
        return response
