from django.contrib import admin
from .models import Auction, AuctionResult, Category, Item, Bid

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    fields = ('name', 'icon', 'desc', 'slug') 
    prepopulated_fields = {"slug": ["name"]}

# Register your models here.
@admin.register(Auction)
class AuctionAdmin(admin.ModelAdmin):
    fieldsets = (
        (("Basic info"), {"fields": ("title", "slug","desc")}),
        (("Pricing"), {"fields": ("entry_fee",)}),
        (("Dating"), {"fields": ("start_date","end_date")}),
        ((None),{"fields":("created_by",)})
    )
    prepopulated_fields = {"slug": ["title"]}
    readonly_fields = ('created_by',)
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
admin.site.register(AuctionResult)
admin.site.register(Item)
admin.site.register(Bid)
