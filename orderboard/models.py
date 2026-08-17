from decimal import Decimal
from django.db import models


# =============================================================================
# CUSTOMER MODEL
# =============================================================================

class Customer(models.Model):

    # -------------------------------------------------------------------------
    # Fields
    # -------------------------------------------------------------------------

    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    postal_code = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # -------------------------------------------------------------------------
    # Methods
    # -------------------------------------------------------------------------

    def __str__(self):
        return self.name


# =============================================================================
# CUSTOMER CONTACT MODEL
# =============================================================================

class CustomerContact(models.Model):

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="contacts")
    platform = models.CharField(max_length=30)
    username = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.platform}: {self.username}"


# =============================================================================
# ORDER MODEL
# =============================================================================

class Order(models.Model):

    # -------------------------------------------------------------------------
    # Status Choices
    # -------------------------------------------------------------------------

    class Status(models.TextChoices):
        MODELING = "modeling", "Modeling Queue"
        PRINT = "print", "Print Queue"
        PAINT = "paint", "Paint Queue"
        DONE = "done", "Done"

    # -------------------------------------------------------------------------
    # Fields
    # -------------------------------------------------------------------------

    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="orders")
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    source = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.MODELING)
    order_received_at = models.DateTimeField(blank=True, null=True)
    deadline = models.DateTimeField(blank=True, null=True)
    total_price = models.DecimalField(max_digits=20, decimal_places=2)
    project_cost = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    cost_details = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # -------------------------------------------------------------------------
    # Payment Methods
    # -------------------------------------------------------------------------

    def total_paid(self):
        return sum((payment.paid_amount for payment in self.payments.all()), Decimal("0.00"))

    def remaining_balance(self):
        remaining = self.total_price - self.total_paid()
        if remaining < 0:
            return Decimal("0.00")
        return remaining

    def payment_status(self):
        paid = self.total_paid()
        if paid <= 0:
            return "Not Paid"
        if paid < self.total_price:
            return "Partially Paid"
        return "Fully Paid"

    # -------------------------------------------------------------------------
    # Display Helpers
    # -------------------------------------------------------------------------

    def is_overdue(self):
        if not self.deadline:
            return False
        if self.status == self.Status.DONE:
            return False
        from django.utils import timezone
        return self.deadline < timezone.now()

    def __str__(self):
        return self.title


# =============================================================================
# ORDER PHOTO MODEL
# =============================================================================

class OrderPhoto(models.Model):

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to="orders/photos/")
    caption = models.CharField(max_length=300, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo for {self.order.title}"


# =============================================================================
# SHIPPING MODEL
# =============================================================================

class Shipping(models.Model):

    # -------------------------------------------------------------------------
    # Status Choices
    # -------------------------------------------------------------------------

    class Status(models.TextChoices):
        NOT_SHIPPED = "not_shipped", "Not Shipped"
        PACKAGED = "packaged", "Packaged"
        SHIPPED = "shipped", "Shipped"
        DELIVERED = "delivered", "Delivered"

    # -------------------------------------------------------------------------
    # Fields
    # -------------------------------------------------------------------------

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="shipping")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NOT_SHIPPED)
    tracking_id = models.CharField(max_length=200, blank=True)
    recipient_name = models.CharField(max_length=60)
    address = models.CharField(max_length=500)
    postal_code = models.CharField(max_length=50, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    shipped_at = models.DateTimeField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Shipping for {self.order.title}"


# =============================================================================
# PAYMENT MODEL
# =============================================================================

class Payment(models.Model):

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payments")
    paid_amount = models.DecimalField(max_digits=20, decimal_places=2)
    note = models.TextField(max_length=500, blank=True)
    paid_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.paid_amount} - {self.order.title}"


# =============================================================================
# ORDER ACTIVITY MODEL
# =============================================================================

class OrderActivity(models.Model):

    class ActivityType(models.TextChoices):
        CREATED = "created", "Order Created"
        UPDATED = "updated", "Order Updated"
        STATUS_CHANGED = "status_changed", "Status Changed"
        PAYMENT = "payment", "Payment Added"
        SHIPPING = "shipping", "Shipping Updated"
        PHOTO = "photo", "Photo Added"
        NOTE = "note", "Note"

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="activities")
    activity_type = models.CharField(max_length=30, choices=ActivityType.choices)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order.title}: {self.message}"