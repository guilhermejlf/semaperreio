import random
import string

from django.db import models
from django.core.validators import MinValueValidator, MaxLengthValidator
from django.utils import timezone
from django.contrib.auth.models import User

def generate_family_code():
    """Generate a 6-character uppercase alphanumeric code."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def default_expiry():
    return timezone.now() + timezone.timedelta(days=7)

class Family(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=6, unique=True, default=generate_family_code)
    code_expires_at = models.DateTimeField(default=default_expiry)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_families')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Family'
        verbose_name_plural = 'Families'

    def __str__(self):
        return self.name

    def regenerate_code(self):
        self.code = generate_family_code()
        self.code_expires_at = timezone.now() + timezone.timedelta(days=7)
        self.save(update_fields=['code', 'code_expires_at'])


class FamilyMembership(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('member', 'Member'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='membership')
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='members')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Family Membership'
        verbose_name_plural = 'Family Memberships'
        unique_together = ['user', 'family']

    def __str__(self):
        return f"{self.user.username} - {self.family.name} ({self.role})"


class Gasto(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gastos')
    family = models.ForeignKey(Family, on_delete=models.SET_NULL, null=True, blank=True, related_name='gastos')
    CATEGORIAS_CHOICES = [
        ('alimentacao', 'Alimentação'),
        ('transporte', 'Transporte'),
        ('moradia', 'Moradia'),
        ('saude', 'Saúde'),
        ('educacao', 'Educação'),
        ('lazer', 'Lazer'),
        ('outros', 'Outros'),
    ]

    valor = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01, message="O valor deve ser maior que zero")]
    )
    categoria = models.CharField(
        max_length=50,
        choices=CATEGORIAS_CHOICES,
        validators=[MaxLengthValidator(50, message="Categoria muito longa")]
    )
    descricao = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        validators=[MaxLengthValidator(200, message="Descrição muito longa")]
    )
    data = models.DateField()
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-data', '-criado_em']
        verbose_name = 'Gasto'
        verbose_name_plural = 'Gastos'

    def __str__(self):
        return f"{self.get_categoria_display()} - R$ {self.valor}"

    def clean(self):
        # Permitir datas futuras para planejamento
        # Apenas validar se a data não é muito antiga
        um_ano_atras = timezone.now().date().replace(year=timezone.now().date().year - 1)
        if self.data < um_ano_atras:
            raise models.ValidationError("A data não pode ser anterior a um ano")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)