from django.urls import path
from .views import *
from . import views

urlpatterns = [
    path("",views.login),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("create/", CreateAccountView.as_view(), name="create"),
    path("deposit/", DepositView.as_view(), name="deposit"),
    path("withdraw/", Withdraw.as_view(), name="withdraw"),
    path("balance/", CheckBalance.as_view(), name="check"),
    path("delete/", DeleteView.as_view(), name="delete"),
    path("login/",views.login),
    path("register/",views.register)
]
