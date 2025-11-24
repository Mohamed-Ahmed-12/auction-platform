from rest_framework.routers import SimpleRouter
from .views import CategoryView , AuctionView , AuctionItemsView
router = SimpleRouter()
router.register(r'category',CategoryView)
router.register(r'auction',AuctionView)
router.register(r'items',AuctionItemsView)

urlpatterns = [
]+router.urls
