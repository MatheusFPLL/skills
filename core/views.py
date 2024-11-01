from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import permission_required # limita o acesso da versão gestor
from django.contrib.auth import views as auth_views
from django.urls import reverse
from .models import Funcionario


def index(request):
    return render(request, 'core/index.html')

def login_view(request):
    # Sua lógica de login padrão aqui
    return render(request, 'core/login.html')

def login_rh(request):
    # Lógica para login como RH (admin)
    return render(request, 'core/login_rh.html')

def login_gestor(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if not user.is_staff:  # Verifica se o usuário não é um admin
                login(request, user)
                return redirect('dashboard_gestor')  # Redireciona para a página do gestor após login
            else:
                messages.error(request, 'Você não tem permissão para acessar como gestor.')
        else:
            messages.error(request, 'Nome de usuário ou senha incorretos.')
    else:
        form = AuthenticationForm()
        
    return render(request, 'core/login_gestor.html', {'form': form})

class GestorLoginView(auth_views.LoginView):
    template_name = 'core/login_gestor.html'  # Caminho para o template de login do gestor

    def get_success_url(self):
        # Redireciona para a URL correspondente ao dashboard do gestor
        return reverse('dashboard_gestor')

def dashboard_gestor(request):
    funcionarios = Funcionario.objects.prefetch_related('skills').all()
    return render(request, 'base_gestor.html', {'funcionarios': funcionarios})