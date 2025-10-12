from django.utils import timezone
from django.db import models 
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db.models import Max
from django.utils.text import slugify
# Create your models here.

User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    icon = models.FileField(upload_to="category", blank=True, null=True)
    desc = models.TextField(blank=True, null=True)
    slug = models.SlugField(max_length=255,null=True,blank=True)

    class Meta:
        verbose_name_plural = "Categories"
        
    def __str__(self):
        return self.name

class Auction(models.Model):
    title = models.CharField(max_length=255)
    desc = models.TextField(blank=True, null=True)

    entry_fee = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.00, message="Entry fee cannot be negative.")]
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(
        validators=[MinValueValidator(timezone.now, message="End date must be in the future.")]
    )
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    slug = models.SlugField(max_length=255,null=True,blank=True)
    
    def __str__(self):
        return self.title
    
    def clean(self):
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValidationError('End time must be after start time.')        
        super().clean()

    # To ensure validation runs before every save, you must call clean() 
    # and handle the ValidationError before calling save().
    def save(self, *args, **kwargs):
        if not self.slug:
            # Generate slug from the title
            self.slug = slugify(self.title) 
        self.full_clean()  # Calls clean_fields(), clean(), and validate_unique()
        super().save(*args, **kwargs)
  
class Item(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="items")
    title = models.CharField(max_length=255)
    desc = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    start_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.00, message="Start price cannot be negative.")]
    )
    min_increment = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01, message="Minimum increment must be a positive amount.")]
    )
    class Meta:
        db_table_comment  = "Auction Items"
        
    
    def __str__(self):
        return self.title



class Bid(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE,related_name="bids")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.created_by} bid {self.amount} on {self.item}"

    # Overriding the clean() method for model-wide validation
    def clean(self):
        
        # 1. Check if the auction is still active
        if self.item.auction.end_date < timezone.now():
            raise ValidationError('The auction has ended and no further bids are accepted.')

        # 2. Check the amount against the current highest bid + min_increment
        
        # Find the highest existing bid amount for this item
        highest_bid_amount = Bid.objects.filter(item=self.item).aggregate(Max('amount'))['amount__max']
        
        # Determine the required minimum bid: start_price if no bids, otherwise highest_bid
        required_minimum_bid = self.item.start_price 
        if highest_bid_amount:
             # If highest_bid_amount exists, the next bid must be higher than it + min_increment
            required_minimum_bid = highest_bid_amount + self.item.min_increment
        else:
             # If no bids exist, the first bid must be >= start_price
             # If the start_price is also less than the min_increment, a sensible rule is:
             required_minimum_bid = max(self.item.start_price, self.item.min_increment)
        
        # Check if the proposed bid amount meets the required minimum
        if self.amount < required_minimum_bid:
            raise ValidationError(
                f'Bid amount must be at least ${required_minimum_bid:.2f} '
                f'(current high bid is ${highest_bid_amount or self.item.start_price:.2f} + min increment of ${self.item.min_increment:.2f})'
            )

        super().clean()

    # To ensure validation runs before every save, you must call clean() 
    # and handle the ValidationError before calling save().
    def save(self, *args, **kwargs):
        self.full_clean()  # Calls clean_fields(), clean(), and validate_unique()
        super().save(*args, **kwargs)
        
class AuctionResult(models.Model):
    item = models.OneToOneField(Item, on_delete=models.CASCADE, related_name="result")
    winner = models.ForeignKey(User, on_delete=models.CASCADE)
    winning_bid = models.ForeignKey(Bid, on_delete=models.CASCADE)
    finalized_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.winner} won {self.item.title} with {self.winning_bid.amount}"
