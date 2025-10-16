from rest_framework.routers import SimpleRouter
from .views import CategoryView , AuctionView
router = SimpleRouter()
router.register(r'category',CategoryView)
router.register(r'auction',AuctionView)
urlpatterns = [

]+router.urls