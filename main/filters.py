from .models import Auction
from django_filters import FilterSet , CharFilter
from django.utils import timezone

class AuctionFilter(FilterSet):
    status = CharFilter(method="filter_by_status",label="Status")
    class Meta:
        model = Auction
        fields = ['status',]
    def filter_by_status(self, queryset, name, value):
        now = timezone.now()
        if value == 'ended':
            return queryset.filter(end_date__lt=now)
        elif value == 'upcoming':
            return queryset.filter(start_date__gt=now)
        elif value == 'live':
            return queryset.filter(start_date__lte=now, end_date__gte=now)
        return queryset