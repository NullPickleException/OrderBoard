from django import forms
from django.forms import inlineformset_factory

from .models import (
    Customer,
    CustomerContact,
    Order,
    Payment,
    Shipping,
    OrderPhoto,
)


# =============================================================================
# CUSTOMER FORM
# =============================================================================

class CustomerForm(forms.ModelForm):

    class Meta:
        model = Customer

        fields = [
            "name",
            "phone",
            "address",
            "postal_code",
        ]

        widgets = {
            "address": forms.Textarea(
                attrs={
                    "rows": 3,
                }
            ),
        }


# =============================================================================
# CUSTOMER CONTACT FORM
# =============================================================================

class CustomerContactForm(forms.ModelForm):

    class Meta:
        model = CustomerContact

        fields = [
            "platform",
            "username",
        ]

        widgets = {
            "platform": forms.TextInput(
                attrs={
                    "placeholder": "Instagram, Telegram, etc.",
                }
            ),
            "username": forms.TextInput(
                attrs={
                    "placeholder": "Username or account",
                }
            ),
        }


# =============================================================================
# CUSTOMER CONTACT FORMSET
# =============================================================================

CustomerContactFormSet = inlineformset_factory(
    Customer,
    CustomerContact,
    form=CustomerContactForm,
    extra=1,
    can_delete=True,
)


# =============================================================================
# ORDER FORM
# =============================================================================

class OrderForm(forms.ModelForm):

    # -------------------------------------------------------------------------
    # Existing Customer
    # -------------------------------------------------------------------------

    customer = forms.ModelChoiceField(
        queryset=Customer.objects.all(),
        required=False,
        widget=forms.HiddenInput(),
    )

    # -------------------------------------------------------------------------
    # New Customer
    # -------------------------------------------------------------------------

    create_customer = forms.BooleanField(
        required=False,
        label="Create new customer",
    )

    new_customer_name = forms.CharField(
        max_length=100,
        required=False,
        label="Customer Name",
    )

    new_customer_phone = forms.CharField(
        max_length=30,
        required=False,
        label="Customer Phone",
    )

    new_customer_address = forms.CharField(
        required=False,
        label="Customer Address",
        widget=forms.Textarea(
            attrs={
                "rows": 3,
            }
        ),
    )

    new_customer_postal_code = forms.CharField(
        max_length=50,
        required=False,
        label="Customer Postal Code",
    )

    class Meta:
        model = Order

        fields = [
            "customer",
            "title",
            "description",
            "source",
            "status",
            "order_received_at",
            "deadline",
            "total_price",
            "project_cost",
            "cost_details",
            "notes",
        ]

        widgets = {
            "description": forms.Textarea(
                attrs={
                    "rows": 4,
                }
            ),

            "cost_details": forms.Textarea(
                attrs={
                    "rows": 3,
                }
            ),

            "notes": forms.Textarea(
                attrs={
                    "rows": 4,
                }
            ),

            "order_received_at": forms.DateTimeInput(
                format="%Y-%m-%dT%H:%M",
                attrs={
                    "type": "datetime-local",
                },
            ),

            "deadline": forms.DateTimeInput(
                format="%Y-%m-%dT%H:%M",
                attrs={
                    "type": "datetime-local",
                },
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["order_received_at"].input_formats = [
            "%Y-%m-%dT%H:%M",
        ]

        self.fields["deadline"].input_formats = [
            "%Y-%m-%dT%H:%M",
        ]

    def clean(self):
        cleaned_data = super().clean()

        create_customer = cleaned_data.get("create_customer")
        customer = cleaned_data.get("customer")

        if create_customer:

            name = cleaned_data.get("new_customer_name")

            if not name:
                self.add_error(
                    "new_customer_name",
                    "Please enter the customer's name.",
                )

        elif not customer:

            self.add_error(
                "customer",
                "Please select a customer or create a new one.",
            )

        return cleaned_data

    def save(self, commit=True):
        order = super().save(commit=False)

        if self.cleaned_data.get("create_customer"):

            customer = Customer.objects.create(
                name=self.cleaned_data["new_customer_name"],
                phone=self.cleaned_data["new_customer_phone"],
                address=self.cleaned_data["new_customer_address"],
                postal_code=self.cleaned_data[
                    "new_customer_postal_code"
                ],
            )

            order.customer = customer

        if commit:
            order.save()

        return order


# =============================================================================
# ORDER EDIT FORM
# =============================================================================

class OrderEditForm(forms.ModelForm):

    class Meta:
        model = Order

        fields = [
            "customer",
            "title",
            "description",
            "source",
            "status",
            "order_received_at",
            "deadline",
            "total_price",
            "project_cost",
            "cost_details",
            "notes",
        ]

        widgets = {
            "description": forms.Textarea(
                attrs={
                    "rows": 4,
                }
            ),

            "cost_details": forms.Textarea(
                attrs={
                    "rows": 3,
                }
            ),

            "notes": forms.Textarea(
                attrs={
                    "rows": 4,
                }
            ),

            "order_received_at": forms.DateTimeInput(
                format="%Y-%m-%dT%H:%M",
                attrs={
                    "type": "datetime-local",
                },
            ),

            "deadline": forms.DateTimeInput(
                format="%Y-%m-%dT%H:%M",
                attrs={
                    "type": "datetime-local",
                },
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["order_received_at"].input_formats = [
            "%Y-%m-%dT%H:%M",
        ]

        self.fields["deadline"].input_formats = [
            "%Y-%m-%dT%H:%M",
        ]


# =============================================================================
# PAYMENT FORM
# =============================================================================

class PaymentForm(forms.ModelForm):

    class Meta:
        model = Payment

        fields = [
            "paid_amount",
            "note",
        ]

        widgets = {
            "note": forms.Textarea(
                attrs={
                    "rows": 3,
                }
            ),
        }

    def __init__(self, *args, order=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.order = order

    def clean_paid_amount(self):
        amount = self.cleaned_data["paid_amount"]

        if amount < 0:
            raise forms.ValidationError(
                "Payment amount cannot be negative."
            )

        if self.order:
            current_amount = self.instance.paid_amount or 0

            remaining = (
                self.order.remaining_balance()
                + current_amount
            )

            if amount > remaining:
                raise forms.ValidationError(
                    f"Payment cannot exceed the remaining balance "
                    f"({remaining})."
                )

        return amount


# =============================================================================
# SHIPPING FORM
# =============================================================================

class ShippingForm(forms.ModelForm):

    class Meta:
        model = Shipping

        fields = [
            "status",
            "tracking_id",
            "recipient_name",
            "address",
            "postal_code",
            "phone",
            "shipped_at",
            "delivered_at",
        ]

        widgets = {
            "shipped_at": forms.DateTimeInput(
                format="%Y-%m-%dT%H:%M",
                attrs={
                    "type": "datetime-local",
                },
            ),

            "delivered_at": forms.DateTimeInput(
                format="%Y-%m-%dT%H:%M",
                attrs={
                    "type": "datetime-local",
                },
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["shipped_at"].input_formats = [
            "%Y-%m-%dT%H:%M",
        ]

        self.fields["delivered_at"].input_formats = [
            "%Y-%m-%dT%H:%M",
        ]


# =============================================================================
# ORDER PHOTO FORM
# =============================================================================

class OrderPhotoForm(forms.ModelForm):

    class Meta:
        model = OrderPhoto

        fields = [
            "image",
            "caption",
        ]

        widgets = {
            "caption": forms.TextInput(),
        }