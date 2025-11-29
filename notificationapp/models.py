from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

User = get_user_model()

# --- Custom Manager for Notifications ---

class NotificationQuerySet(models.QuerySet):
    """Custom QuerySet to add common notification queries."""
    def unread(self):
        """Returns all unread notifications."""
        return self.filter(is_read=False)

    def read(self):
        """Returns all read notifications."""
        return self.filter(is_read=True)
    
    def mark_all_as_read(self, user):
        """Marks all unread notifications for a specific user as read."""
        return self.filter(user=user, is_read=False).update(is_read=True)

class NotificationManager(models.Manager):
    """Custom Manager to inject the custom QuerySet."""
    def get_queryset(self):
        return NotificationQuerySet(self.model, using=self._db)
    
    # Expose custom methods on the Manager as well
    def unread(self):
        # Usage : Notification.objects.unread()
        return self.get_queryset().unread()

# --- Notification Categories ---

class NotificationCategories(models.TextChoices):
    # Group: AUCTION ACTIVITY
    AUCTION_JOINED = 'ROOM_JOINED', "Joined Bidding Room"
    AUCTION_LEFT = 'ROOM_LEFT', "Left Bidding Room"
    AUCTION_CREATED = 'AUCTION_CREATED', "Auction Has Been Created"
    AUCTION_OUTBID = 'OUTBID', "You have been outbid"
    AUCTION_WON = 'AUCTION_WON', "Auction Won"
    
    # Group: SYSTEM/ADMIN ALERTS
    SYSTEM_UPDATE = 'SYSTEM_UPDATE', "System Maintenance"

    def get_group(self):
        """Helper to return a broad category group for frontend filtering."""
        if self in [self.AUCTION_JOINED, self.AUCTION_LEFT, self.AUCTION_CREATED, self.AUCTION_OUTBID, self.AUCTION_WON]:
            return 'AUCTION_ACTIVITY'
        return 'GENERAL_ALERT'

# --- Notification Model ---

class Notification(models.Model):
    # Custom Manager
    objects = NotificationManager()
    
    # The RECIPIENT of the notification (who should see it)
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='notifications_received',
        verbose_name="Recipient"
    ) 
    
    # The entity that CAUSED the notification (e.g., the user who joined, the admin)
    sender = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='notifications_sent',
        verbose_name="Sender (Causer)"
    )
    
    # The TYPE of event
    category = models.CharField(
        max_length=50, 
        choices=NotificationCategories.choices, 
        blank=False, 
        null=False
    )
    
    # --- Generic Foreign Key for the related object (e.g., Auction, Bid) ---
    content_type = models.ForeignKey(
        ContentType, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        help_text="The type of the related object (e.g., 'Auction', 'Bid')."
    )
    object_id = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text="The primary key of the related object."
    )
    # The actual field to access the related object
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # The final, rendered message (Optional: can be pre-rendered or left blank for frontend rendering)
    content = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        help_text="The pre-rendered notification message."
    )

    # --- Status & Timestamps ---
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __str__(self):
        return f"Notif for {self.user.username} ({self.get_category_display()})"
    
    # --- Content Generation and Save Override ---
    
    def generate_content(self):
        """Generates the notification content based on category and related objects."""
        category_display = self.get_category_display()
        
        # You'll need access to the related object (content_object) or sender for richer messages.
        sender_name = self.sender.username if self.sender else 'System'
        
        if self.category == NotificationCategories.AUCTION_CREATED:
            # Assumes content_object is the Auction model
            auction_title = getattr(self.content_object, 'title', 'an item') if self.content_object else 'an auction'
            return f"**{auction_title}** has been created!"
        
        elif self.category == NotificationCategories.AUCTION_JOINED: 
            return f"**{sender_name}** {category_display}."
        
        elif self.category == NotificationCategories.AUCTION_OUTBID:
            # Assumes content_object is the Auction model
            auction_title = getattr(self.content_object, 'title', 'an auction') if self.content_object else 'your item'
            return f"You have been **outbid** on **{auction_title}**!"
        
        elif self.category == NotificationCategories.SYSTEM_UPDATE: 
            return f"{category_display}: Check out the latest changes!"
        
        # Default fallback
        return f"Alert: {category_display}"

    def save(self, *args, **kwargs):
        """Override save to automatically generate content on creation."""
        # Only generate content on the initial creation (when pk is None) 
        # OR if you specifically want to regenerate it (e.g., if you remove the content check)
        if not self.pk and not self.content:
            self.content = self.generate_content()
        
        super().save(*args, **kwargs)