import jwt
from django.conf import settings
from django.shortcuts import redirect
from django.http import HttpResponse


class LoginRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        token = request.COOKIES.get("token")

        if not token:
            return redirect("/login/")

        try:
            jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return HttpResponse("Session expired. Please login again.", status=401)
        except:
            return redirect("/login/")
        
        return super().dispatch(request, *args, **kwargs)



class AdminRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        token = request.COOKIES.get("token")

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            if payload.get("role") != "admin":
                return HttpResponse("Unauthorized! Admins only.", status=403)
        except:
            return redirect("/login/")
        
        return super().dispatch(request, *args, **kwargs)
