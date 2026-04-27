from rest_framework import serializers
from django.utils import timezone
from .models import Gasto

class GastoSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    is_group = serializers.SerializerMethodField()

    class Meta:
        model = Gasto
        fields = ['id', 'user', 'valor', 'categoria', 'descricao', 'data', 'user_name', 'is_group', 'criado_em', 'atualizado_em']
        read_only_fields = ['id', 'user', 'criado_em', 'atualizado_em']
    
    def to_representation(self, instance):
        # Garantir formatação correta das datas
        data = super().to_representation(instance)
        
        # Formatar data para ISO sem timezone info
        if data.get('data'):
            data['data'] = instance.data.strftime('%Y-%m-%d')
            
        # Formatar datetime para ISO
        if data.get('criado_em'):
            data['criado_em'] = instance.criado_em.isoformat()
            
        if data.get('atualizado_em'):
            data['atualizado_em'] = instance.atualizado_em.isoformat()
            
        return data

    def validate_valor(self, value):
        if value <= 0:
            raise serializers.ValidationError("O valor deve ser maior que zero")
        if value > 999999.99:
            raise serializers.ValidationError("O valor máximo permitido é R$ 999.999,99")
        return value

    def validate_data(self, value):
        # Permitir datas futuras com aviso (planejamento)
        # Limitar a não mais que 1 ano no passado
        um_ano_atras = timezone.now().date().replace(year=timezone.now().date().year - 1)
        if value < um_ano_atras:
            raise serializers.ValidationError("A data não pode ser anterior a um ano")
        return value

    def validate_categoria(self, value):
        categorias_validas = [choice[0] for choice in Gasto.CATEGORIAS_CHOICES]
        if value not in categorias_validas:
            raise serializers.ValidationError("Categoria inválida")
        return value

    def validate_descricao(self, value):
        if value and len(value.strip()) == 0:
            return ""
        return value.strip() if value else value

    def get_user_name(self, obj):
        return obj.user.username if obj.user else None

    def get_is_group(self, obj):
        return obj.family is not None