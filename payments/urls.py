from django.urls import path
from . import views

app_name = "payments"

urlpatterns = [
    path("initiate/<int:order_id>/", views.initiate_payment, name="initiate_payment"),
    path("verify/<int:payment_id>/", views.verify_payment, name="verify_payment"),
]
