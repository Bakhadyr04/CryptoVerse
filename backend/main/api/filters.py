import django_filters
from main.models import Order

class OrderFilter(django_filters.FilterSet):
    price_min = django_filters.NumberFilter(field_name="price", lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name="price", lookup_expr='lte')
    created_after = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='lte')

    class Meta:
        model = Order
        fields = ['type', 'status', 'price_min', 'price_max', 'created_after', 'created_before']

# Фильтр по типу и статусу - http://127.0.0.1:8000/api/orders/?type=buy&status=completed
# Фильтр по диапазону цен  - http://127.0.0.1:8000/api/orders/?price_min=10000&price_max=30000
# Фильтр по дате создания  - http://127.0.0.1:8000/api/orders/?created_after=2025-06-10
# Комбинированный запрос   - http://127.0.0.1:8000/api/orders/?type=sell&price_max=50000&created_before=2025-06-10
