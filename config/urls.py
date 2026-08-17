"""
URL configuration for config project.
"""

from django.contrib import admin
from django.urls import include, path


urlpatterns = [

    # =========================================================================
    # Django Admin
    # =========================================================================

    path(
        "admin/",
        admin.site.urls,
    ),

    # =========================================================================
    # Authentication
    # =========================================================================

    path(
        "accounts/",
        include("django.contrib.auth.urls"),
    ),

    # =========================================================================
    # OrderBoard
    # =========================================================================

    path(
        "",
        include("orderboard.urls"),
    ),
]