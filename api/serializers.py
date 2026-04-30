from rest_framework import serializers
from django.utils import timezone
from .models import Gasto, Receita, MetaGasto

class GastoSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    is_group = serializers.SerializerMethodField()

    class Meta:
        model = Gasto
        fields = ['id', 'user', 'valor', 'categoria', 'descricao', 'data', 'data_competencia', 'data_pagamento', 'pago', 'user_name', 'is_group', 'criado_em', 'atualizado_em']
        read_only_fields = ['id', 'user', 'criado_em', 'atualizado_em']
    
    def to_representation(self, instance):
        # Garantir formatação correta das datas
        data = super().to_representation(instance)
        
        # Formatar data para ISO sem timezone info
        if data.get('data'):
            data['data'] = instance.data.strftime('%Y-%m-%d')
        if data.get('data_competencia') and instance.data_competencia:
            data['data_competencia'] = instance.data_competencia.strftime('%Y-%m-%d')
        if data.get('data_pagamento') and instance.data_pagamento:
            data['data_pagamento'] = instance.data_pagamento.strftime('%Y-%m-%d')
            
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

    def validate_data_competencia(self, value):
        if value:
            um_ano_atras = timezone.now().date().replace(year=timezone.now().date().year - 1)
            if value < um_ano_atras:
                raise serializers.ValidationError("A data de competência não pode ser anterior a um ano")
        return value

    def validate_data_pagamento(self, value):
        if value:
            um_ano_atras = timezone.now().date().replace(year=timezone.now().date().year - 1)
            if value < um_ano_atras:
                raise serializers.ValidationError("A data de pagamento não pode ser anterior a um ano")
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


class ReceitaSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    is_group = serializers.SerializerMethodField()

    class Meta:
        model = Receita
        fields = ['id', 'user', 'valor', 'descricao', 'data', 'user_name', 'is_group', 'criado_em', 'atualizado_em']
        read_only_fields = ['id', 'user', 'criado_em', 'atualizado_em']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if data.get('data'):
            data['data'] = instance.data.strftime('%Y-%m-%d')
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
        um_ano_atras = timezone.now().date().replace(year=timezone.now().date().year - 1)
        if value < um_ano_atras:
            raise serializers.ValidationError("A data não pode ser anterior a um ano")
        return value

    def validate_descricao(self, value):
        if value and len(value.strip()) == 0:
            return ""
        return value.strip() if value else value

    def get_user_name(self, obj):
        return obj.user.username if obj.user else None

    def get_is_group(self, obj):
        return obj.family is not None


class MetaGastoSerializer(serializers.ModelSerializer):
    gasto_realizado = serializers.SerializerMethodField()
    percentual_usado = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    categoria_nome = serializers.SerializerMethodField()

    class Meta:
        model = MetaGasto
        fields = ['id', 'categoria', 'categoria_nome', 'mes', 'ano', 'valor_meta', 'gasto_realizado', 'percentual_usado', 'status', 'criado_em', 'atualizado_em']
        read_only_fields = ['id', 'criado_em', 'atualizado_em']

    def get_gasto_realizado(self, obj):
        from django.db.models import Sum
        gastos = Gasto.objects.filter(
            user=obj.user,
            categoria=obj.categoria if obj.categoria else None,
            data_competencia__month=obj.mes,
            data_competencia__year=obj.ano
        )
        if obj.categoria is None:
            gastos = Gasto.objects.filter(
                user=obj.user,
                data_competencia__month=obj.mes,
                data_competencia__year=obj.ano
            )
        total = gastos.aggregate(total=Sum('valor'))['total'] or 0
        return round(float(total), 2)

    def get_percentual_usado(self, obj):
        gasto = self.get_gasto_realizado(obj)
        if obj.valor_meta and float(obj.valor_meta) > 0:
            return round((gasto / float(obj.valor_meta)) * 100, 1)
        return 0.0

    def get_status(self, obj):
        pct = self.get_percentual_usado(obj)
        if pct > 100:
            return 'critical'
        elif pct > 80:
            return 'danger'
        elif pct > 50:
            return 'warning'
        return 'ok'

    def get_categoria_nome(self, obj):
        if obj.categoria:
            return obj.get_categoria_display()
        return 'Geral'