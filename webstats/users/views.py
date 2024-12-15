from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages


# Create your views here.
def register(Request):
    if Request.method == "POST":
        Form = UserCreationForm(Request.POST)
        if Form.is_valid():
            UserObject = Form.save()
            login(Request, UserObject)
            messages.success(Request, "Registration successful.")
            return redirect("home")
        else:
            messages.error(Request, "Unsuccessful registration. Invalid information.")
    else:
        Form = UserCreationForm()
    return render(Request, "users/register.html", {"form": Form})


def userLogin(Request):
    if Request.method == "POST":
        Form = AuthenticationForm(Request, data=Request.POST)
        if Form.is_valid():
            Username = Form.cleaned_data.get("username")
            Password = Form.cleaned_data.get("password")
            UserObject = authenticate(username=Username, password=Password)
            if UserObject is not None:
                login(Request, UserObject)
                messages.success(Request, f"Welcome back, {UserObject.username}!")
                return redirect("home")
            else:
                messages.error(Request, "Invalid username or password.")
        else:
                messages.error(Request, "Invalid username or password.")
    else:
        Form = AuthenticationForm()
    return render(Request, "users/login.html", {"form": Form})

def userLogout(Request):
    logout(Request)
    return redirect("home")