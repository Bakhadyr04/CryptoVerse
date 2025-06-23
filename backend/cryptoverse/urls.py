from django.contrib import admin
from django.urls import path, include
from main.views import active_users_last_24h, bulk_delete_old_promotions, bulk_update_promotions, cryptocurrency_api, login_view, order_transactions_view, participate, non_admin_users, promotion_stats, promotion_titles_values, recent_transactions, index, search_promotions, total_transaction_amount, transactions_by_active_promotions, user_transaction_sums, user_promotion_counts
from main.views import PromotionDetailView
from main.api.views import RegisterView

from main import views
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.authtoken.views import obtain_auth_token


urlpatterns = [
    path('admin/', admin.site.urls),
    path("", index, name="home"),
    path('api/', include('main.api.urls')),
    path('api/token/', obtain_auth_token, name='api_token_auth'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', login_view, name='login'),
    path("order-transactions/<int:order_id>/", order_transactions_view),
    path("participate/<int:promo_id>/", participate, name="participate"),
    path("non-admin-users/", non_admin_users, name="non_admin_users"),
    path("recent-transactions/", recent_transactions, name="recent_transactions"),
    path("active-last-24h/", active_users_last_24h, name="active_last_24h"),
    path("promotions/<int:pk>/", PromotionDetailView.as_view(), name="promotion_detail"),
    path("total-transaction-amount/", total_transaction_amount),
    path("user-transaction-sums/", user_transaction_sums),
    path("user-promotion-counts/", user_promotion_counts),
    path('promotions/', views.promotions_list, name='promotions_list'),
    path('promotions/add/', views.add_promotion, name='add_promotion'),
    path('promotions/delete/<int:pk>/', views.delete_promotion, name='delete_promotion'),
    path('promotions/edit/<int:pk>/', views.edit_promotion, name='edit_promotion'),
    path('promotions/<int:pk>/', views.promotion_detail_redirect, name='promotion_detail'),
    path('promotions/search/', search_promotions, name='search_promotions'),
    path("promotions/values/", promotion_titles_values),
    path("transactions/by-active-promotions/", transactions_by_active_promotions, name="transactions_by_active_promotions"),
    path("promotions/stats/", promotion_stats),
    path("promotions/bulk-update/", bulk_update_promotions),
    path("promotions/bulk-delete/", bulk_delete_old_promotions),
    path('cryptocurrencies/', cryptocurrency_api, name='cryptocurrency_api'),
    path('promotions-api/', views.promotions_api, name='promotions_api'),
    path('recent-users/', views.recent_users_api, name='recent_users_api'),
    path('cryptocurrencies/add/', views.cryptocurrency_add, name='cryptocurrency_add'),
    path('cryptocurrencies/<int:pk>/update/', views.cryptocurrency_update, name='cryptocurrency_update'),
    path('cryptocurrencies/<int:pk>/delete/', views.cryptocurrency_delete, name='cryptocurrency_delete'),
    path('cryptocurrencies/<int:pk>/', views.cryptocurrency_detail, name='cryptocurrency_detail'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# Маршрут с ошибкой для проверки Sentry - http://localhost:8000/sentry-debug/
# def trigger_error(request):
#     division_by_zero = 1 / 0

# urlpatterns += [
#     path("sentry-debug/", trigger_error),
# ]

# Silk
if settings.DEBUG:
    urlpatterns += [path('silk/', include('silk.urls', namespace='silk'))]