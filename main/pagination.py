from rest_framework.pagination import PageNumberPagination

class AuctionItemPagination(PageNumberPagination):
    page_size=1
