from django.urls import path
from .views import *
from . import views

urlpatterns = [
    path("",views.login),
    path("AllCustomers/",AllCustomersView.as_view(),name="AllCustomers"),
    path("Registered_users/",AdminUsersListView.as_view(), name="Registered_users"),
    path("promote_user/<int:user_id>/", PromoteAdminView.as_view(), name="promote_user"),
    path("delete_user/<int:user_id>/", AdminDeleteUserView.as_view(), name="delete_user"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("Admin_dashboard/", AdminDashboardView.as_view(), name="Admin_dashboard"),
    path("create/", CreateAccountView.as_view(), name="create"),
    path("deposit/", DepositView.as_view(), name="deposit"),
    path("withdraw/", Withdraw.as_view(), name="withdraw"),
    path("balance/", CheckBalance.as_view(), name="check"),
    path("delete/", DeleteView.as_view(), name="delete"),
    path("login/",views.login),
    path("register/",views.register)
]
