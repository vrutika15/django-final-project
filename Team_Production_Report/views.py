from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse


def landing(request):
    if request.method == 'POST':
        choice = request.POST.get('choice')
        if choice == 'user':
            request.session['role'] = 'user'
            return redirect('dashboard')
        return redirect('login')
    return render(request, 'landing.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is None:
            messages.error(request, 'Invalid credentials')
            return render(request, 'login.html')

        login(request, user)
        if username == 'superadmin':
            request.session['role'] = 'superadmin'
            return redirect('dashboard')
        if username == 'admin':
            request.session['role'] = 'admin'
            return redirect('dashboard')

        # default 
        request.session['role'] = 'user'
        return redirect('dashboard')

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    request.session.pop('role', None)
    return redirect('landing')


def user_home(request):
    if request.session.get('role') != 'user':
        request.session['role'] = 'user'
    return redirect('dashboard')


@login_required
def admin_home(request):
    request.session['role'] = 'admin'
    return redirect('dashboard')


@login_required
def superadmin_home(request):
    request.session['role'] = 'superadmin'
    return redirect('dashboard')


