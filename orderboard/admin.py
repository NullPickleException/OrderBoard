from django.contrib import admin

# Register your models here.
from .models import (
    Customer,
    CustomerContact,
    Order,
    OrderPhoto,
    Shipping,
    Payment,
)


admin.site.register(Customer)
admin.site.register(CustomerContact)
admin.site.register(Order)
admin.site.register(OrderPhoto)
admin.site.register(Shipping)
admin.site.register(Payment)