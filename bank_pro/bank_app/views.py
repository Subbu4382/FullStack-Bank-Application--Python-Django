from django.views.generic import TemplateView, CreateView, FormView, DeleteView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from .models import Account, User
import cloudinary
from django.views import View
from .serializer import AccountSerializer
from django.contrib.auth.hashers import make_password, check_password
from .models import User
import jwt
from .mixins import LoginRequiredMixin, AdminRequiredMixin
from django.conf import settings
import environ
import datetime 
from datetime import date
env = environ.Env()
environ.Env.read_env()
from django.core.mail import EmailMessage




class AllCustomersView(AdminRequiredMixin,View):
    def get(self,req):
       AllCustomers=Account.objects.all()
       return render(req,"AllCustomers.html",{"AllCustomers":AllCustomers})

class AdminUsersListView(AdminRequiredMixin, TemplateView):
    template_name = "Register_user_list.html"

    def get(self, request):
        users = User.objects.all()
        return render(request, self.template_name, {"users": users})


class PromoteAdminView(AdminRequiredMixin,View):
    def get(self,request, user_id):
       user = User.objects.get(id=user_id)
       user.role = "admin"
       user.save()

       return redirect("Registered_users")

    
class AdminDeleteUserView(AdminRequiredMixin, View):

    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            # prevent deleting admins
            if user.role == "admin":
                return render(request, "error.html", {
                "message": "Admin accounts cannot be deleted."
            })

            user.delete()
            return redirect("Registered_users")

        except Exception as e:
         return render(request, "login.html", {"error": str(e)})
    



class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"

class AdminDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "Admin_dashboard.html"

class CreateAccountView(LoginRequiredMixin, CreateView):
    model = Account
    fields = ["name", "email", "phone", "balance", "account_type"]
    template_name = "create_account.html"
    success_url = reverse_lazy("dashboard")

    def form_valid(self, form):
        account = form.save()
        # Upload photo
        uploaded_photo = self.request.FILES.get("photo")
        if uploaded_photo:
            result = cloudinary.uploader.upload(uploaded_photo)
            account.photo = result["secure_url"]

        account.save()

        try:
            if account.email:
                email = EmailMessage(
                    subject="SFC Bank",
                    body=(
                        f"Dear {account.name},\n\n"
                        f"Your new SFC Bank account has been successfully created.\n"
                        f"Account Number: {account.account_number}\n"
                        f"Thank you for choosing SFC Bank."
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[account.email],
                )
                email.send()
                print("mail sent sucessfully")
        except Exception as e:
            print("EMAIL ERROR:", str(e)) 

        return render(
            self.request,
            "success.html",
            {"msg": "Account Created Successfully!", "account": account},
        )



class DepositView(LoginRequiredMixin, View):
    template_name = "deposit.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):

        acc_no = request.POST.get("account_number")
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        ifsc = request.POST.get("ifsc")
        branch = request.POST.get("branch")
        amount = request.POST.get("amount")

        try:
            amount = float(amount)
            if amount <= 0:
                raise Exception("Amount must be greater than 0")
        except:
            return render(request, self.template_name, {"error": "Invalid Amount"})

    
        try:
            user = Account.objects.get(account_number=acc_no)
        except Account.DoesNotExist:
            return render(request, self.template_name, {"error": "Account Not Found"})

        # Validate user-entered details
        errors = []

        if user.name != name:
            errors.append("Name does not match our records")
        if user.phone != phone:
            errors.append("Phone number does not match our records")
        if user.email != email:
            errors.append("Email does not match our records")
        if user.ifsc_code != ifsc:
            errors.append("IFSC code incorrect")
        if user.branch_name != branch:
            errors.append("Branch name incorrect")

        if errors:
            return render(request, self.template_name, {"error": errors})

        # Update balance
        new_balance = user.balance + amount

        # Serializer validation
        serializer = AccountSerializer(
            user, data={"balance": new_balance}, partial=True
        )

        if serializer.is_valid():
            serializer.save()
            if user.email:
                email = EmailMessage(
                    subject="SFC Bank",
                    body=(
                        f"Dear {user.name},\n\n"
                        f"We are pleased to inform you that an amount of ₹{amount} has been "
                        f"successfully credited to your account.\n\n"
                        f"Account Number : XXXXXX{user.account_number[-4:]}\n"
                        f"Current Balance : ₹{new_balance}\n\n"
                        f"If you have not initiated this transaction, please contact your branch immediately.\n\n"
                        f"Regards,\n"
                        f"SFC Bank"
                    ),
                    from_email="subrahmanyamdunne02@gmail.com",
                    to=[user.email],
                )
           
            email.send()
            print("email send sucessfully")
            return render(
                request,
                "success.html",
                {
                    "msg": f"Dear {user.name}, an amount of ₹{amount} has been credited to your account",
                    "user": user,
                },
            )
        print(user)

        return render(request, self.template_name, {"error": serializer.errors})


class Withdraw(LoginRequiredMixin, View):
    template_name = "withdraw.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):

        acc_no = request.POST.get("account_number")
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        ifsc = request.POST.get("ifsc")
        branch = request.POST.get("branch")
        amount = request.POST.get("amount")

        # Fetch account
        try:
            user = Account.objects.get(account_number=acc_no)
        except Account.DoesNotExist:
            return render(request, self.template_name, {"error": "Account Not Found"})

        # Validate user details with DB
        errors = []

        if user.name != name:
            errors.append("Name does not match our records")
        if user.phone != phone:
            errors.append("Phone number does not match our records")
        if user.email != email:
            errors.append("Email does not match our records")
        if user.ifsc_code != ifsc:
            errors.append("Invalid IFSC code")
        if user.branch_name != branch:
            errors.append("Invalid Branch name")

        if errors:
            return render(request, self.template_name, {"error": errors})

        # Validate amount format
        try:
            amount = float(amount)
        except:
            return render(request, self.template_name, {"error": "Invalid Amount"})
        if amount <= 0:
            return render(
                request, self.template_name, {"error": "Amount must be greater than 0"}
            )
        # Check balance
        if user.balance < amount:
            return render(
                request, self.template_name, {"error": "Insufficient Balance"}
            )
        # Calculate new balance
        new_balance = user.balance - amount

        # Serializer: update only balance
        serializer = AccountSerializer(
            user, data={"balance": new_balance}, partial=True
        )

        if serializer.is_valid():
            serializer.save()
            if user.email:
                email = EmailMessage(
                    subject="SFC Bank",
                    body=(
                        f"Dear {user.name},\n\n"
                        f"An amount of ₹{amount} has been debited from your account "
                        f"on {datetime.date.today().strftime('%d-%m-%Y')} at "
                        f"{datetime.datetime.now().strftime('%I:%M %p')}.\n\n"
                        f"Account Number : XXXXXXXX{user.account_number[-4:]}\n"
                        f"Available Balance : ₹{new_balance}\n\n"
                        "If this transaction was not initiated by you, "
                        "please contact SFC Bank customer support immediately.\n\n"
                        "Thank you for banking with us.\n"
                        "SFC Bank"
                    ),
                    from_email="subrahmanyamdunne02@gmail.com",
                    to=[user.email],
                )
           
            email.send()
            print("email send sucessfully")
            message = (
                f"Dear {user.name}, an amount of ₹{amount} has been debited from your Account"
            )
            return render(
                request,
                "success.html",
                {
                    "msg": message,
                    "user": user,
                },
            )

        return render(request, self.template_name, {"error": serializer.errors})


class CheckBalance(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, "check_balance.html")

    def post(self, request):
        acc_no = request.POST.get("account_number")

        try:
            acc = Account.objects.get(account_number=acc_no)
            return render(
                request,
                "check_balance.html",
                {"balance": acc.balance, "acc_no": acc.account_number},
            )
        except Account.DoesNotExist:
            return render(request, "check_balance.html", {"error": "Account Not Found"})


class DeleteView(AdminRequiredMixin, View):

    def get(self, request):
        return render(request, "delete.html")

    def post(self, request):
        name = request.POST.get("name")  # or email
        try:
            user = User.objects.get(name=name)
            user.delete()
            return render(
                request, "delete.html", {"success": "User deleted successfully"}
            )
        except User.DoesNotExist:
            return render(request, "delete.html", {"error": "User not found"})


SECRET_KEY = settings.SECRET_KEY


def register(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")

        # default role (no radio button)
        role = "user"

        # Check if email exists
        if User.objects.filter(email=email).exists():
            return render(
                request, "register.html", {"error": "Email already registered"}
            )

        # Create user
        User.objects.create(
            name=name, email=email, password=make_password(password), role=role
        )

        return render(request, "register.html", {"success": "Registration successful!"})

    return render(request, "register.html")


ADMIN_EMAIL = env("ADMIN_EMAIL")
ADMIN_PASSWORD = env("ADMIN_PASSWORD")
def login(request):
    if request.method == "POST":

        login_type = request.POST.get("login_type")
        email = request.POST.get("email")
        password = request.POST.get("password")

        # ======================================================
        #                 ADMIN LOGIN
        # ======================================================
        if login_type == "admin":

            # 1️⃣ First check FIXED ADMIN credentials
            if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
                payload = {
                    "email": email,
                    "role": "admin",
                    "is_admin": True,
                    "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
                }
                token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
                response = redirect("Admin_dashboard")
                response.set_cookie("token", token, httponly=True)
                return response

            # 2️⃣ If not fixed admin → Check admin in User Database
            try:
                user = User.objects.get(email=email, role="admin")
            except User.DoesNotExist:
                return render(request, "login.html", {"message": "Admin account not found"})

            # Check password
            if not check_password(password, user.password):
                return render(request, "login.html", {"message": "Invalid admin password"})

            # Create token
            payload = {
                "email": user.email,
                "name": user.name,
                "role": "admin",
                "is_admin": True,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
            }

            token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

            response = redirect("Admin_dashboard")
            response.set_cookie("token", token, httponly=True)
            return response

        # ======================================================
        #                 USER LOGIN
        # ======================================================
        if login_type == "user":

            try:
                user = User.objects.get(email=email, role="user")
            except User.DoesNotExist:
                return render(request, "login.html", {"message": "User account not found"})

            # Check password
            if not check_password(password, user.password):
                return render(request, "login.html", {"message": "Invalid user password"})

            # Create token
            payload = {
                "email": user.email,
                "name": user.name,
                "role": "user",
                "is_admin": False,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
            }

            token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

            response = redirect("dashboard")
            response.set_cookie("token", token, httponly=True)
            return response

    # GET request → show login page
    return render(request, "login.html")
