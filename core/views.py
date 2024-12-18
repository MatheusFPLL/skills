from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Funcionario, Notificacao
from .models import Treinamento, FuncionarioSkill
import csv
from django.db.models import Prefetch

def index(request):
    """
    Página inicial com opções de login para RH e Gestor.
    """
    return render(request, 'core/index.html')


def login_rh(request):
    """
    Login para usuários do tipo RH.
    """
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if hasattr(user, 'funcionario') and user.funcionario.is_rh:
                login(request, user)
                return redirect('admin:index')  # Redireciona para o admin do Django
            else:
                return render(
                    request,
                    'core/login_rh.html',
                    {'form': form, 'error': 'Usuário não autorizado como RH.'}
                )
    else:
        form = AuthenticationForm()
    return render(request, 'core/login_rh.html', {'form': form})


def login_gestor(request):
    """
    Login para usuários do tipo Gestor.
    """
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if hasattr(user, 'funcionario') and user.funcionario.is_gestor:
                login(request, user)
                return redirect('gestor_dashboard')  # Certifique-se de que essa URL está correta
            else:
                return render(
                    request, 
                    'core/login_gestor.html', 
                    {'form': form, 'error': 'Usuário não autorizado como Gestor.'}
                )
    else:
        form = AuthenticationForm()
    return render(request, 'core/login_gestor.html', {'form': form})


@login_required
def gestor_dashboard(request):
    """
    Dashboard para gestores, exibindo apenas funcionários do setor do gestor.
    """
    # Verifica se o usuário logado está associado a um Funcionario
    try:
        funcionario = Funcionario.objects.get(usuario=request.user)
    except Funcionario.DoesNotExist:
        return HttpResponse("Acesso não autorizado", status=403)

    # Verifica se o funcionário é um gestor
    if not funcionario.is_gestor:
        return HttpResponse("Acesso não autorizado", status=403)

    # Recupera o setor do gestor e os funcionários do setor
    setor_do_gestor = funcionario.setor
    funcionarios = Funcionario.objects.filter(setor=setor_do_gestor)

    return render(request, 'core/gestor_dashboard.html', {
        'funcionarios': funcionarios,
        'setor': setor_do_gestor
    })


@login_required
def exportar_funcionarios(request):
    """
    Exporta funcionários em um arquivo CSV.
    """
    # Garante que somente usuários autorizados podem exportar
    if not request.user.is_staff and not (hasattr(request.user, 'funcionario') and request.user.funcionario.is_rh):
        return HttpResponse("Acesso negado", status=403)

    # Configura a resposta como CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="funcionarios.csv"'

    writer = csv.writer(response)
    writer.writerow(['Nome', 'Setor', 'Cargo', 'Data de Contratação', 'Treinamento Concluído', 'Skills'])

    # Obtém os funcionários
    funcionarios = Funcionario.objects.select_related('setor', 'cargo').prefetch_related('skills')
    for funcionario in funcionarios:
        skills = ", ".join(skill.nome for skill in funcionario.skills.all())
        writer.writerow([
            funcionario.nome,
            funcionario.setor.nome if funcionario.setor else "Sem Setor",
            funcionario.cargo.nome if funcionario.cargo else "Sem Cargo",
            funcionario.data_contratacao,
            "Sim" if funcionario.comprovacao_treinamento else "Não",
            skills
        ])

    return response


# Função utilitária para verificar se um usuário é um gestor
def usuario_eh_gestor(user):
    """
    Retorna True se o usuário for um gestor.
    """
    return hasattr(user, 'funcionario') and user.funcionario.is_gestor


@login_required
def notificacoes(request):
    """
    Exibe as notificações para o usuário logado.
    """
    # Verifica se o usuário está autenticado
    if not request.user.is_authenticated:
        return redirect('login')  # Redireciona para a página de login

    # Obtém o funcionário associado ao usuário logado
    try:
        funcionario = Funcionario.objects.get(usuario=request.user)
    except Funcionario.DoesNotExist:
        return HttpResponse("Funcionário não encontrado", status=404)

    # Acesse as notificações do usuário diretamente através do campo 'usuario'
    notificacoes = Notificacao.objects.filter(usuario=request.user)

    return render(request, 'admin/notificacoes.html', {
        'notificacoes': notificacoes
    })


@login_required
def marcar_notificacao_lida(request, notificacao_id):
    """
    Marca a notificação como lida.
    """
    try:
        notificacao = request.user.funcionario.notificacoes.get(id=notificacao_id)
        notificacao.lida = True
        notificacao.save()
        return redirect('notificacoes')  # Redireciona de volta para a lista de notificações
    except Funcionario.DoesNotExist:
        return HttpResponse("Funcionario não encontrado", status=404)
    except Notificacao.DoesNotExist:
        return HttpResponse("Notificação não encontrada", status=404)


@login_required
def exportar_funcionarios(request):
    """
    Exporta funcionários em um arquivo CSV.
    """
    # Garante que somente usuários autorizados podem exportar
    if not request.user.is_staff and not (hasattr(request.user, 'funcionario') and request.user.funcionario.is_rh):
        return HttpResponse("Acesso negado", status=403)

    # Configura a resposta como CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="funcionarios.csv"'

    writer = csv.writer(response)
    writer.writerow(['Nome', 'Setor', 'Cargo', 'Data de Contratação', 'Treinamento Concluído', 'Skills'])

    # Obtém os funcionários
    funcionarios = Funcionario.objects.select_related('setor', 'cargo').prefetch_related('skills')
    for funcionario in funcionarios:
        skills = ", ".join(skill.nome for skill in funcionario.skills.all())
        writer.writerow([
            funcionario.nome,
            funcionario.setor.nome if funcionario.setor else "Sem Setor",
            funcionario.cargo.nome if funcionario.cargo else "Sem Cargo",
            funcionario.data_contratacao,
            "Sim" if funcionario.comprovacao_treinamento else "Não",
            skills
        ])

    return response


# Função utilitária para verificar se um usuário é um gestor
def usuario_eh_gestor(user):
    """
    Retorna True se o usuário for um gestor.
    """
    return hasattr(user, 'funcionario') and user.funcionario.is_gestor

@login_required
def treinamentos(request):
    """
    Exibe os treinamentos associados ao funcionário logado.
    """
    try:
        funcionario = Funcionario.objects.get(usuario=request.user)
    except Funcionario.DoesNotExist:
        return HttpResponse("Funcionário não encontrado", status=404)

    # Recupera os treinamentos do funcionário
    treinamentos = Treinamento.objects.filter(funcionarios=funcionario)

    return render(request, 'core/treinamentos.html', {
        'treinamentos': treinamentos,
        'funcionario': funcionario,
    })

def listar_treinamentos(request):
    treinamentos = Treinamento.objects.prefetch_related(
        Prefetch('funcionarios', queryset=Funcionario.objects.prefetch_related(
            Prefetch('funcionarioskill_set', queryset=FuncionarioSkill.objects.select_related('skill'))
        ))
    )
    return render(request, 'core/listar_treinamentos.html', {'treinamentos': treinamentos})

@login_required
def listar_skills(request, funcionario_id):
    try:
        funcionario = Funcionario.objects.get(id=funcionario_id)
    except Funcionario.DoesNotExist:
        return HttpResponse("Funcionário não encontrado", status=404)

    # Acessar skills com informações adicionais através de FuncionarioSkill
    skills_com_niveis = FuncionarioSkill.objects.filter(funcionario=funcionario)

    return render(request, 'core/listar_skills.html', {
        'funcionario': funcionario,
        'skills_com_niveis': skills_com_niveis,  # Passa para o template
    })

@login_required
def adicionar_skill(request, funcionario_id):
    try:
        funcionario = Funcionario.objects.get(id=funcionario_id)
    except Funcionario.DoesNotExist:
        return HttpResponse("Funcionário não encontrado", status=404)

    if request.method == 'POST':
        skill_id = request.POST.get('skill_id')
        nivel = request.POST.get('nivel', 1)  # Nível padrão é 1
        try:
            skill = Skill.objects.get(id=skill_id)
        except Skill.DoesNotExist:
            return HttpResponse("Skill não encontrada", status=404)

        # Criar ou atualizar a relação no FuncionarioSkill
        FuncionarioSkill.objects.update_or_create(
            funcionario=funcionario,
            skill=skill,
            defaults={'nivel': nivel}
        )
        return redirect('listar_skills', funcionario_id=funcionario.id)

    skills_disponiveis = Skill.objects.all()
    return render(request, 'core/adicionar_skill.html', {
        'funcionario': funcionario,
        'skills': skills_disponiveis,
    })
