from django import forms
from django.contrib import admin
from django.db.models import Q
from .models import Funcionario, Skill, Setor, Cargo, FuncionarioSkill, Treinamento
from django.contrib.auth.models import User, Group
import csv
from django.http import HttpResponse

# Remover User e Group do admin
admin.site.unregister(User)
admin.site.unregister(Group)

# Personalizar o título do site admin
admin.site.site_header = "Skills Enforce"
admin.site.site_title = "Gestão de Skills Admin"
admin.site.index_title = "Bem-vindo à Gestão de Skills"
admin.site.index_template = "admin/index.html"

# Função para exportar funcionários em CSV
def exportar_funcionarios_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="funcionarios.csv"'
    writer = csv.writer(response)

    # Cabeçalhos do CSV
    writer.writerow(['Nome', 'Setor', 'Cargo', 'Data de Contratação', 'Treinamento Concluído', 'Skills e Níveis'])

    # Dados dos funcionários selecionados
    for funcionario in queryset.select_related('setor', 'cargo').prefetch_related('funcionarioskill_set__skill'):
        skills = ", ".join(
            f"{rel.skill.nome} (Nível: {rel.nivel})"
            for rel in funcionario.funcionarioskill_set.all()
        )
        writer.writerow([
            funcionario.nome,
            funcionario.setor.nome if funcionario.setor else "Sem Setor",
            funcionario.cargo.nome if funcionario.cargo else "Sem Cargo",
            funcionario.data_contratacao,
            "Sim" if funcionario.comprovacao_treinamento else "Não",
            skills,
        ])

    return response

exportar_funcionarios_csv.short_description = "Exportar selecionados para CSV"

# Configuração do admin para Skills
@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao')
    search_fields = ('nome',)

# Configuração do admin para Cargos
@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'setor', 'competencias', 'escopo_atividade')
    search_fields = ('nome',)
    list_filter = ('setor',)

# Inline para FuncionarioSkill com campo de nível
class FuncionarioSkillInline(admin.TabularInline):
    model = FuncionarioSkill
    extra = 1
    fields = ('skill', 'nivel', 'data_adicao')
    readonly_fields = ('data_adicao',)

# Configuração do admin para Setores
@admin.register(Setor)
class SetorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'get_funcionarios', 'get_cargos')
    search_fields = ('nome',)

    def get_funcionarios(self, obj):
        return ", ".join([funcionario.nome for funcionario in obj.funcionario_set.all()])
    get_funcionarios.short_description = 'Funcionários'

    def get_cargos(self, obj):
        return ", ".join(set(funcionario.cargo.nome for funcionario in obj.funcionario_set.all() if funcionario.cargo))
    get_cargos.short_description = 'Cargos'

@admin.register(Treinamento)
class TreinamentoAdmin(admin.ModelAdmin):
    list_display = ('nome_funcionarios', 'skills_treinadas', 'data_inicio', 'data_fim', 'finalizado')
    search_fields = ('funcionarios__nome', 'skills__nome')
    list_filter = ('finalizado', 'data_inicio')
    filter_horizontal = ('skills', 'funcionarios')  # Para facilitar seleção no ManyToMany

    # Reorganizar os campos no formulário
    fields = ('funcionarios', 'skills', 'data_inicio', 'data_fim', 'finalizado')

    def nome_funcionarios(self, obj):
        """
        Retorna os nomes dos funcionários associados ao treinamento.
        """
        return ", ".join([funcionario.nome for funcionario in obj.funcionarios.all()])
    nome_funcionarios.short_description = 'Funcionários'

    def skills_treinadas(self, obj):
        """
        Retorna as skills associadas ao treinamento com o nível atual de cada funcionário.
        """
        skills_info = []
        for funcionario in obj.funcionarios.all():
            for relacao in funcionario.funcionarioskill_set.all():
                if relacao.skill in obj.skills.all():  # Filtrar apenas skills relacionadas ao treinamento
                    skills_info.append(f"{relacao.skill.nome} (Nível Atual: {relacao.nivel}, Próximo: {relacao.nivel + 1})")
        return "; ".join(skills_info)
    skills_treinadas.short_description = 'Skills e Níveis'

    def get_queryset(self, request):
        """
        Otimiza o queryset para evitar consultas excessivas.
        """
        qs = super().get_queryset(request)
        return qs.prefetch_related('funcionarios__funcionarioskill_set__skill')

# Configuração do admin para Funcionários
@admin.register(Funcionario)
class FuncionarioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cargo', 'setor', 'data_contratacao', 'get_skills_with_nivel', 'comprovacao_treinamento' )
    search_fields = ('nome', 'cargo__nome')
    list_filter = ('cargo', 'comprovacao_treinamento')
    inlines = [FuncionarioSkillInline]
    actions = [exportar_funcionarios_csv]

    fieldsets = (
        (None, {
            'fields': ('nome', 'setor', 'cargo', 'data_contratacao', 'comprovacao_treinamento')
        }),
    )

    def get_skills_with_nivel(self, obj):
        skills = obj.funcionarioskill_set.select_related('skill').all()
        return ", ".join([f"{skill.skill.nome} (Nível: {skill.nivel})" for skill in skills])
    get_skills_with_nivel.short_description = 'Skills e Níveis'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        try:
            funcionario = request.user.funcionario
            if funcionario.is_rh:
                return qs
            elif funcionario.is_gestor:
                return qs.filter(setor=funcionario.setor)
        except Funcionario.DoesNotExist:
            return qs.none()
        return qs.none()

    def has_add_permission(self, request):
        try:
            return request.user.funcionario.is_rh
        except Funcionario.DoesNotExist:
            return False

    def has_change_permission(self, request, obj=None):
        try:
            funcionario = request.user.funcionario
            if funcionario.is_rh:
                return True
            if funcionario.is_gestor:
                return obj and obj.setor == funcionario.setor
        except Funcionario.DoesNotExist:
            return False
        return False

    def has_delete_permission(self, request, obj=None):
        try:
            return request.user.funcionario.is_rh
        except Funcionario.DoesNotExist:
            return False
