from .models import Auction
from django_filters import FilterSet , CharFilter , BaseInFilter
from django.utils import timezone
from django.db.models import Q
class AuctionFilter(FilterSet):
    status = CharFilter(method="filter_by_status",label="Status")
    category = BaseInFilter(field_name="category__slug", lookup_expr="in", label="Category")
    class Meta:
        model = Auction
        fields = ['category']
    def filter_by_status(self, queryset, name, value):
        now = timezone.now()

        # split the incoming value "live,upcoming"
        statuses = [v.strip() for v in value.split(',') if v.strip()]

        q = Q()

        if 'ended' in statuses:
            q |= Q(end_date__lt=now)

        if 'upcoming' in statuses:
            q |= Q(start_date__gt=now)

        if 'live' in statuses:
            q |= Q(start_date__lte=now, end_date__gt=now)

        if q:
            return queryset.filter(q)

        return queryset