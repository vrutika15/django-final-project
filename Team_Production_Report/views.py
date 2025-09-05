from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse


def landing(request):
    """
    Landing page with choices: User or Admin.
    - User: set session role to 'user' and go to user site.
    - Admin: go to login page.
    """
    if request.method == 'POST':
        choice = request.POST.get('choice')
        if choice == 'user':
            request.session['role'] = 'user'
            return redirect('dashboard')
        return redirect('login')
    return render(request, 'landing.html')


def login_view(request):
    """
    Username-based role login with no signup.
    - username 'admin' => role=admin
    - username 'superadmin' => role=superadmin
    Other usernames are not used here.
    """
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

        # default safeguard
        request.session['role'] = 'user'
        return redirect('dashboard')

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    request.session.pop('role', None)
    return redirect('landing')


def user_home(request):
    # user site entrypoint → project list with limited write actions
    # Ensure a role exists
    if request.session.get('role') != 'user':
        request.session['role'] = 'user'
    return redirect('dashboard')


@login_required
def admin_home(request):
    # Admin has full CRUD access; redirect to dashboard
    request.session['role'] = 'admin'
    return redirect('dashboard')


@login_required
def superadmin_home(request):
    # Superadmin has read-only access; redirect to dashboard
    request.session['role'] = 'superadmin'
    return redirect('dashboard')


