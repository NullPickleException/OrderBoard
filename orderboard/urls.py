from django.urls import path

from . import views


urlpatterns = [

    # =========================================================================
    # Dashboard
    # =========================================================================

    path(
        "",
        views.dashboard,
        name="dashboard",
    ),

    # =========================================================================
    # Export
    # =========================================================================

    path(
        "export/",
        views.export_center,
        name="export_center",
    ),

    path(
        "export/excel/",
        views.export_excel,
        name="export_excel",
    ),

    # =========================================================================
    # Orders
    # =========================================================================

    path(
        "orders/",
        views.order_list,
        name="order_list",
    ),

    path(
        "orders/create/",
        views.order_create,
        name="order_create",
    ),

    path(
        "orders/<int:id>/",
        views.order_detail,
        name="order_detail",
    ),

    path(
        "orders/<int:id>/edit/",
        views.order_edit,
        name="order_edit",
    ),

    path(
        "orders/<int:id>/delete/",
        views.order_delete,
        name="order_delete",
    ),

    # =========================================================================
    # Payments
    # =========================================================================

    path(
        "payments/",
        views.payment_list,
        name="payment_list",
    ),

    path(
        "orders/<int:id>/payment/",
        views.payment_create,
        name="payment_create",
    ),

    path(
        "payments/<int:id>/edit/",
        views.payment_edit,
        name="payment_edit",
    ),

    path(
        "payments/<int:id>/delete/",
        views.payment_delete,
        name="payment_delete",
    ),

    # =========================================================================
    # Shipping
    # =========================================================================

    path(
        "shipping/",
        views.shipping_list,
        name="shipping_list",
    ),

    path(
        "shipping/<int:id>/edit/",
        views.shipping_edit,
        name="shipping_edit",
    ),

    # =========================================================================
    # Printing
    # =========================================================================

    path(
        "printing/",
        views.printing_list,
        name="printing_list",
    ),

    # =========================================================================
    # Photos
    # =========================================================================

    path(
        "orders/<int:id>/photos/upload/",
        views.photo_upload,
        name="photo_upload",
    ),

    path(
        "photos/<int:id>/delete/",
        views.photo_delete,
        name="photo_delete",
    ),

    # =========================================================================
    # Customers
    # =========================================================================

    path(
        "customers/",
        views.customer_list,
        name="customer_list",
    ),

    path(
        "customers/create/",
        views.customer_create,
        name="customer_create",
    ),

    path(
        "customers/search/",
        views.customer_search,
        name="customer_search",
    ),

    path(
        "customers/<int:id>/",
        views.customer_detail,
        name="customer_detail",
    ),

    path(
        "customers/<int:id>/edit/",
        views.customer_edit,
        name="customer_edit",
    ),

    path(
        "customers/<int:id>/delete/",
        views.customer_delete,
        name="customer_delete",
    ),
]