import pickle
import pandas as pd
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
import os
import logging

from django.db import models
from django.db.models import Q
from .models import Gasto, FamilyMembership
from .serializers import GastoSerializer
from .permissions import GastoPermission

logger = logging.getLogger(__name__)

# -------------------------
# MODELO IA (Lazy Loading)
# -------------------------
_modelo_ia = None

def get_modelo_ia():
    global _modelo_ia
    if _modelo_ia is None:
        try:
            caminho_modelo = os.path.join(os.path.dirname(__file__), "modelo.pkl")
            with open(caminho_modelo, "rb") as f:
                _modelo_ia = pickle.load(f)
            logger.info("Modelo IA carregado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao carregar modelo IA: {e}")
            _modelo_ia = None
    return _modelo_ia

# -------------------------
# IA - PREVISÃO
# -------------------------
@api_view(["POST"])
def prever_gasto(request):
    try:
        mes = request.data.get("mes")
        
        # Validação do mês
        if mes is None:
            return Response(
                {"erro": "Informe o mês (1-12)", "campo": "mes"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            mes_int = int(mes)
            if mes_int < 1 or mes_int > 12:
                return Response(
                    {"erro": "Mês deve estar entre 1 e 12", "campo": "mes"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (ValueError, TypeError):
            return Response(
                {"erro": "Mês deve ser um número válido", "campo": "mes"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Carregar modelo e fazer previsão
        modelo = get_modelo_ia()
        if modelo is None:
            return Response(
                {"erro": "Serviço de previsão indisponível no momento"}, 
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        entrada = pd.DataFrame({"mes": [mes_int]})
        previsao = modelo.predict(entrada)
        
        # Limitar previsão a valores razoáveis
        previsao_valor = max(0, min(float(previsao[0]), 100000))

        return Response({
            "mes": mes_int,
            "previsao": round(previsao_valor, 2),
            "moeda": "BRL"
        })

    except Exception as e:
        logger.error(f"Erro na previsão: {e}")
        return Response(
            {"erro": "Erro interno no servidor"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# -------------------------
# GASTOS CRUD
# -------------------------
def get_user_family(user):
    """Get the family of the current user, or None."""
    try:
        return user.membership.family
    except AttributeError:
        return None

@api_view(['GET', 'POST'])
def gastos(request):
    try:
        if request.method == 'GET':
            user_family = get_user_family(request.user)
            
            if user_family:
                # User has family: show family gastos + own gastos without family
                queryset = Gasto.objects.filter(
                    Q(family=user_family) | Q(user=request.user, family__isnull=True)
                )
            else:
                # No family: only own gastos
                queryset = Gasto.objects.filter(user=request.user)
            
            # Filtro por categoria
            categoria = request.query_params.get('categoria')
            if categoria:
                queryset = queryset.filter(categoria=categoria)
            
            # Filtro por período
            data_inicio = request.query_params.get('data_inicio')
            data_fim = request.query_params.get('data_fim')
            if data_inicio:
                queryset = queryset.filter(data__gte=data_inicio)
            if data_fim:
                queryset = queryset.filter(data__lte=data_fim)
            
            # Ordenação e limite
            queryset = queryset.order_by('-data', '-criado_em')
            
            # Paginação simples
            limite = int(request.query_params.get('limite', 50))
            if limite > 100:
                limite = 100
            queryset = queryset[:limite]
            
            serializer = GastoSerializer(queryset, many=True)
            return Response({
                "gastos": serializer.data,
                "total": len(serializer.data)
            })

        elif request.method == 'POST':
            serializer = GastoSerializer(data=request.data)
            
            if serializer.is_valid():
                family = get_user_family(request.user)
                gasto = serializer.save(user=request.user, family=family)
                return Response(
                    serializer.data, 
                    status=status.HTTP_201_CREATED
                )
            
            # Formatar erros de validação
            errors = {}
            for field, messages in serializer.errors.items():
                errors[field] = messages[0] if isinstance(messages, list) else str(messages)
            
            return Response(
                {"erro": "Dados inválidos", "detalhes": errors}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    except Exception as e:
        logger.error(f"Erro na API de gastos: {e}")
        return Response(
            {"erro": "Erro interno no servidor"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET', 'PUT', 'DELETE'])
def gasto_detail(request, pk):
    try:
        gasto = Gasto.objects.get(pk=pk)
    except Gasto.DoesNotExist:
        return Response(
            {"erro": "Gasto não encontrado"}, 
            status=status.HTTP_404_NOT_FOUND
        )

    # Check permission
    permission = GastoPermission()
    if not permission.has_object_permission(request, None, gasto):
        return Response(
            {"erro": "Você não tem permissão para acessar este gasto."},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        if request.method == 'GET':
            serializer = GastoSerializer(gasto)
            return Response(serializer.data)

        elif request.method == 'PUT':
            # Only creator or admin (with post-join check) can edit
            if gasto.user != request.user:
                # Check admin permission with post-join validation
                membership = get_user_family(request.user)
                if not membership or membership.role != 'admin':
                    return Response(
                        {"erro": "Você não tem permissão para editar este gasto."},
                        status=status.HTTP_403_FORBIDDEN
                    )
                # Check if gasto was created after user joined
                if not FamilyMembership.objects.filter(
                    family=membership,
                    user=gasto.user,
                    joined_at__lte=gasto.criado_em
                ).exists():
                    return Response(
                        {"erro": "Você não pode editar gastos criados antes de seu ingresso no grupo."},
                        status=status.HTTP_403_FORBIDDEN
                    )

            serializer = GastoSerializer(gasto, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            
            errors = {}
            for field, messages in serializer.errors.items():
                errors[field] = messages[0] if isinstance(messages, list) else str(messages)
            
            return Response(
                {"erro": "Dados inválidos", "detalhes": errors}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        elif request.method == 'DELETE':
            # Same permission logic as PUT
            if gasto.user != request.user:
                membership = get_user_family(request.user)
                if not membership or membership.role != 'admin':
                    return Response(
                        {"erro": "Você não tem permissão para excluir este gasto."},
                        status=status.HTTP_403_FORBIDDEN
                    )
                if not FamilyMembership.objects.filter(
                    family=membership,
                    user=gasto.user,
                    joined_at__lte=gasto.criado_em
                ).exists():
                    return Response(
                        {"erro": "Você não pode excluir gastos criados antes de seu ingresso no grupo."},
                        status=status.HTTP_403_FORBIDDEN
                    )

            gasto.delete()
            return Response(
                {"mensagem": "Gasto excluído com sucesso"}, 
                status=status.HTTP_204_NO_CONTENT
            )

    except Exception as e:
        logger.error(f"Erro no detalhe do gasto: {e}")
        return Response(
            {"erro": "Erro interno no servidor"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )