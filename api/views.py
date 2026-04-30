import pandas as pd
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
import logging
from calendar import monthrange

from django.db import models
from django.db.models import Q, Sum, Count, Max
from django.db.models.functions import Coalesce, TruncMonth
from decimal import Decimal
from .models import Gasto, FamilyMembership, Receita, Family, MetaGasto
from .serializers import GastoSerializer, ReceitaSerializer, MetaGastoSerializer
from .permissions import GastoPermission

logger = logging.getLogger(__name__)

# -------------------------
# IA - PREVISÃO COM DADOS REAIS (por categoria)
# -------------------------
from sklearn.linear_model import LinearRegression
import numpy as np
from collections import defaultdict


def _treinar_modelo_temporal(totais_por_mes):
    """
    Treina LinearRegression com índice temporal como feature.
    totais_por_mes: lista ordenada de floats (total do mês)
    Retorna modelo treinado ou None se insuficiente.
    """
    n = len(totais_por_mes)
    if n < 2:
        return None
    X = np.arange(n).reshape(-1, 1)
    y = np.array([float(v) for v in totais_por_mes])
    modelo = LinearRegression()
    modelo.fit(X, y)
    return modelo


def _prever_serie(serie, mes_alvo_idx):
    """
    Prevê valor para um índice temporal alvo dado uma série histórica.
    Fallback: < 3 meses -> média simples.
    Retorna (valor, modo).
    """
    n = len(serie)
    if n == 0:
        return 0.0, "sem_dados"
    if n < 3:
        media = sum(float(v) for v in serie) / n
        return media, "media"
    modelo = _treinar_modelo_temporal(serie)
    if modelo is None:
        return 0.0, "sem_dados"
    valor = max(0.0, float(modelo.predict(np.array([[mes_alvo_idx]]))[0]))
    return valor, "modelo"


def _construir_serie_categoria(meses_unicos, dados_categoria):
    """
    Constrói série temporal completa (meses faltantes = 0) para uma categoria.
    """
    return [dados_categoria.get(m, 0.0) for m in meses_unicos]


@api_view(["POST"])
def prever_gasto(request):
    try:
        mes = request.data.get("mes")
        ano = request.data.get("ano")

        queryset = get_user_gastos_queryset(request.user)

        # Agrupar por (ano, mes, categoria)
        categoria_map = defaultdict(lambda: defaultdict(float))
        for g in queryset:
            data = g.data_efetiva
            if data:
                categoria_map[g.categoria][(data.year, data.month)] += float(g.valor)

        if not categoria_map:
            return Response(
                {"erro": "Nenhum gasto encontrado para previsão. Cadastre gastos e tente novamente."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Meses únicos ordenados (união de todos os meses de todas as categorias)
        meses_unicos = sorted({
            (ano, mes)
            for cat_dict in categoria_map.values()
            for (ano, mes) in cat_dict.keys()
        })

        n_meses = len(meses_unicos)
        if n_meses < 1:
            return Response(
                {"erro": "Nenhum gasto encontrado para previsão. Cadastre gastos e tente novamente."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Determinar mês alvo
        ultimo_ano, ultimo_mes = meses_unicos[-1]
        if ano is not None and mes is not None:
            try:
                mes_alvo = int(mes)
                ano_alvo = int(ano)
            except (ValueError, TypeError):
                return Response(
                    {"erro": "Mês e ano devem ser números válidos"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            if ultimo_mes == 12:
                mes_alvo = 1
                ano_alvo = ultimo_ano + 1
            else:
                mes_alvo = ultimo_mes + 1
                ano_alvo = ultimo_ano

        # Índice do mês alvo no eixo temporal (após o último mês conhecido)
        distancia = (ano_alvo - ultimo_ano) * 12 + (mes_alvo - ultimo_mes)
        mes_alvo_idx = n_meses - 1 + distancia

        # Prever por categoria
        categorias_labels = dict(Gasto.CATEGORIAS_CHOICES)
        previsao_por_categoria = {}
        total_previsto = 0.0
        modos_usados = set()

        for cat_key, cat_dict in categoria_map.items():
            serie = _construir_serie_categoria(meses_unicos, cat_dict)
            valor, modo = _prever_serie(serie, mes_alvo_idx)
            previsao_por_categoria[categorias_labels.get(cat_key, cat_key)] = round(valor, 2)
            total_previsto += valor
            if modo != "sem_dados":
                modos_usados.add(modo)

        # Determinar modo geral
        modo_geral = "modelo" if "modelo" in modos_usados else "media"

        # Dados históricos para contexto (total por mês, últimos 6)
        historico = []
        for (a, m) in meses_unicos[-6:]:
            total_mes = sum(cat_dict.get((a, m), 0.0) for cat_dict in categoria_map.values())
            historico.append({"ano": a, "mes": m, "total": round(total_mes, 2)})

        total_previsto = max(0, min(total_previsto, 1000000))

        return Response({
            "previsao": round(total_previsto, 2),
            "mes": mes_alvo,
            "ano": ano_alvo,
            "moeda": "BRL",
            "modo": modo_geral,
            "por_categoria": previsao_por_categoria,
            "dados_historicos": historico,
            "meses_de_dados": n_meses,
            "mensagem": (
                "Previsão baseada em média simples (poucos dados)." if modo_geral == "media"
                else "Previsão baseada em tendência dos últimos meses por categoria."
            )
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

def get_user_membership(user):
    """Get the family membership of the current user, or None."""
    try:
        return user.membership
    except AttributeError:
        return None

def get_user_gastos_queryset(user):
    """Get gastos queryset for user with effective date (data_competencia fallback to data)."""
    user_family = get_user_family(user)
    if user_family:
        queryset = Gasto.objects.filter(
            Q(family=user_family) | Q(user=user, family__isnull=True)
        )
    else:
        queryset = Gasto.objects.filter(user=user)

    return queryset.annotate(
        data_efetiva=Coalesce('data_competencia', 'data')
    )

@api_view(['GET', 'POST'])
def gastos(request):
    try:
        if request.method == 'GET':
            queryset = get_user_gastos_queryset(request.user)

            # Filtro por categoria
            categoria = request.query_params.get('categoria')
            if categoria:
                queryset = queryset.filter(categoria=categoria)

            # Filtro por período (data efetiva = data_competencia com fallback para data)
            data_inicio = request.query_params.get('data_inicio')
            data_fim = request.query_params.get('data_fim')
            if data_inicio:
                queryset = queryset.filter(data_efetiva__gte=data_inicio)
            if data_fim:
                queryset = queryset.filter(data_efetiva__lte=data_fim)

            # Filtro por data de competência explícita
            competencia_inicio = request.query_params.get('competencia_inicio')
            competencia_fim = request.query_params.get('competencia_fim')
            if competencia_inicio:
                queryset = queryset.filter(data_competencia__gte=competencia_inicio)
            if competencia_fim:
                queryset = queryset.filter(data_competencia__lte=competencia_fim)

            # Filtro por data de pagamento
            pagamento_inicio = request.query_params.get('pagamento_inicio')
            pagamento_fim = request.query_params.get('pagamento_fim')
            if pagamento_inicio:
                queryset = queryset.filter(data_pagamento__gte=pagamento_inicio)
            if pagamento_fim:
                queryset = queryset.filter(data_pagamento__lte=pagamento_fim)

            # Filtro por status pago
            pago = request.query_params.get('pago')
            if pago is not None:
                queryset = queryset.filter(pago=pago.lower() in ('true', '1', 'yes', 'sim'))

            # Ordenação e limite (por data efetiva)
            queryset = queryset.order_by('-data_efetiva', '-criado_em')

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
            dados = request.data.copy()
            # Se data_competencia não informado, copiar de data
            if not dados.get('data_competencia') and dados.get('data'):
                dados['data_competencia'] = dados['data']
            # Se pago não informado, setar como False
            if 'pago' not in dados:
                dados['pago'] = False

            serializer = GastoSerializer(data=dados)

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
            dados = request.data.copy()
            # Se data_competencia não informado, manter o existente ou copiar de data
            if not dados.get('data_competencia'):
                if dados.get('data'):
                    dados['data_competencia'] = dados['data']
                else:
                    dados['data_competencia'] = gasto.data_competencia or gasto.data

            serializer = GastoSerializer(gasto, data=dados)
            if serializer.is_valid():
                # Verificar permissão para editar
                if gasto.user != request.user:
                    user_membership = get_user_membership(request.user)
                    if not user_membership or user_membership.role != 'admin':
                        return Response(
                            {"erro": "Você não tem permissão para editar este gasto."},
                            status=status.HTTP_403_FORBIDDEN
                        )

                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"erro": "Dados inválidos", "detalhes": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )

        elif request.method == 'DELETE':
            # Same permission logic as PUT
            if gasto.user != request.user:
                user_membership = get_user_membership(request.user)
                if not user_membership or user_membership.role != 'admin':
                    return Response(
                        {"erro": "Você não tem permissão para excluir este gasto."},
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


@api_view(['GET', 'PUT', 'DELETE'])
def receita_detail(request, pk):
    try:
        receita = Receita.objects.get(pk=pk)
    except Receita.DoesNotExist:
        return Response(
            {"erro": "Receita não encontrada"}, 
            status=status.HTTP_404_NOT_FOUND
        )

    # Check permission - same logic as gasto
    permission = GastoPermission()
    if not permission.has_object_permission(request, None, receita):
        return Response(
            {"erro": "Você não tem permissão para acessar esta receita."},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        if request.method == 'GET':
            serializer = ReceitaSerializer(receita)
            return Response(serializer.data)

        elif request.method == 'PUT':
            dados = request.data.copy()
            serializer = ReceitaSerializer(receita, data=dados)
            if serializer.is_valid():
                if receita.user != request.user:
                    user_membership = get_user_membership(request.user)
                    if not user_membership or user_membership.role != 'admin':
                        return Response(
                            {"erro": "Você não tem permissão para editar esta receita."},
                            status=status.HTTP_403_FORBIDDEN
                        )

                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"erro": "Dados inválidos", "detalhes": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )

        elif request.method == 'DELETE':
            if receita.user != request.user:
                user_membership = get_user_membership(request.user)
                if not user_membership or user_membership.role != 'admin':
                    return Response(
                        {"erro": "Você não tem permissão para excluir esta receita."},
                        status=status.HTTP_403_FORBIDDEN
                    )

            receita.delete()
            return Response(
                {"mensagem": "Receita excluída com sucesso"}, 
                status=status.HTTP_204_NO_CONTENT
            )

    except Exception as e:
        logger.error(f"Erro no detalhe da receita: {e}")
        return Response(
            {"erro": "Erro interno no servidor"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# -------------------------
# DASHBOARD
# -------------------------
MES_NOMES = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
]

@api_view(['GET'])
def dashboard(request):
    try:
        mes = request.query_params.get('mes')
        ano = request.query_params.get('ano')

        if mes is None or ano is None:
            return Response(
                {"erro": "Informe os parâmetros 'mes' (1-12) e 'ano' (YYYY)"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            mes_int = int(mes)
            ano_int = int(ano)
            if mes_int < 1 or mes_int > 12:
                return Response(
                    {"erro": "Mês deve estar entre 1 e 12"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (ValueError, TypeError):
            return Response(
                {"erro": "Mês e ano devem ser números válidos"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Base queryset com filtro de family/user + data efetiva anotada
        base_queryset = get_user_gastos_queryset(request.user)

        # Período atual (por data efetiva = data_competencia com fallback para data)
        queryset_atual = base_queryset.filter(data_efetiva__month=mes_int, data_efetiva__year=ano_int)

        # Período anterior
        if mes_int == 1:
            mes_ant, ano_ant = 12, ano_int - 1
        else:
            mes_ant, ano_ant = mes_int - 1, ano_int
        queryset_anterior = base_queryset.filter(data_efetiva__month=mes_ant, data_efetiva__year=ano_ant)

        # Agregações do período atual
        agg_atual = queryset_atual.aggregate(
            total=Sum('valor'),
            quantidade=Count('id'),
            maior=Max('valor')
        )

        # Agregações do período anterior
        agg_anterior = queryset_anterior.aggregate(
            total=Sum('valor')
        )

        total_mes = agg_atual['total'] or Decimal('0.00')
        total_anterior = agg_anterior['total'] or Decimal('0.00')

        # Base queryset de receitas (mesmo filtro family/user)
        user_family = get_user_family(request.user)
        if user_family:
            receitas_queryset = Receita.objects.filter(
                Q(family=user_family) | Q(user=request.user, family__isnull=True)
            )
        else:
            receitas_queryset = Receita.objects.filter(user=request.user)

        # Total de receitas no período (por data)
        receitas_agg = receitas_queryset.filter(
            data__month=mes_int, data__year=ano_int
        ).aggregate(total=Sum('valor'))
        total_receitas = receitas_agg['total'] or Decimal('0.00')

        # Total de gastos pagos no período (por data_pagamento)
        gastos_pagos_agg = base_queryset.filter(
            data_pagamento__month=mes_int,
            data_pagamento__year=ano_int,
            pago=True
        ).aggregate(total=Sum('valor'))
        total_gastos_pagos = gastos_pagos_agg['total'] or Decimal('0.00')

        # Total a pagar (gastos não pagos do período atual)
        pendentes_agg = queryset_atual.filter(pago=False).aggregate(
            total=Sum('valor'),
            quantidade=Count('id')
        )
        total_a_pagar = pendentes_agg['total'] or Decimal('0.00')
        quantidade_pendentes = pendentes_agg['quantidade'] or 0

        # Saldo
        saldo = total_receitas - total_gastos_pagos

        # Previsão de saldo até o fim do mês
        saldo_projetado = saldo - total_a_pagar
        if total_a_pagar > 0:
            if saldo_projetado < 0:
                previsao_mensagem = f"Se você não tiver novas receitas, seu saldo ficará negativo em R$ {float(abs(saldo_projetado)):.2f}"
            else:
                previsao_mensagem = f"Mesmo com as contas pendentes, você ainda terá R$ {float(saldo_projetado):.2f} disponíveis"
        else:
            previsao_mensagem = None

        # Variacao
        if total_anterior > 0:
            variacao_absoluta = total_mes - total_anterior
            variacao_percentual = (variacao_absoluta / total_anterior) * 100
        else:
            variacao_absoluta = Decimal('0.00')
            variacao_percentual = Decimal('0.00')

        # Maior gasto
        maior_gasto_obj = queryset_atual.order_by('-valor').first()
        maior_gasto = None
        if maior_gasto_obj:
            maior_gasto = {
                "valor": float(maior_gasto_obj.valor),
                "categoria": maior_gasto_obj.get_categoria_display(),
                "descricao": maior_gasto_obj.descricao or ""
            }

        # Ranking de categorias (apenas com gastos)
        ranking = (
            queryset_atual
            .values('categoria')
            .annotate(
                total=Sum('valor'),
                quantidade=Count('id')
            )
            .filter(total__gt=0)
            .order_by('-total')
        )

        total_categorias = sum(item['total'] for item in ranking) or Decimal('1.00')
        ranking_categorias = [
            {
                "categoria": item['categoria'],
                "nome": dict(Gasto.CATEGORIAS_CHOICES).get(item['categoria'], item['categoria']),
                "total": float(item['total']),
                "quantidade": item['quantidade'],
                "percentual": round(float(item['total'] / total_categorias) * 100, 1)
            }
            for item in ranking
        ]

        # Evolução mensal comparativa (últimos 12 meses)
        meses_labels = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
                        'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        evolucao_mensal = []
        for i in range(11, -1, -1):
            m = mes_int - i
            a = ano_int
            while m <= 0:
                m += 12
                a -= 1

            # Gastos do mês (por data_efetiva = data_competencia com fallback)
            gastos_agg = base_queryset.filter(
                data_efetiva__month=m, data_efetiva__year=a
            ).aggregate(total=Sum('valor'))
            total_gastos_mes = gastos_agg['total'] or Decimal('0.00')

            # Receitas do mês (por data)
            receitas_agg = receitas_queryset.filter(
                data__month=m, data__year=a
            ).aggregate(total=Sum('valor'))
            total_receitas_mes = receitas_agg['total'] or Decimal('0.00')

            evolucao_mensal.append({
                "mes": meses_labels[m - 1],
                "ano": a,
                "receitas": float(total_receitas_mes),
                "gastos": float(total_gastos_mes)
            })

        # Média diária
        dias_no_mes = monthrange(ano_int, mes_int)[1]
        media_diaria = float(total_mes) / dias_no_mes if dias_no_mes > 0 else 0.0

        # Metas de gasto
        metas_context = _build_metas_context(request.user, mes_int, ano_int)

        return Response({
            "periodo": {
                "mes": mes_int,
                "ano": ano_int,
                "mes_nome": MES_NOMES[mes_int - 1]
            },
            "total_mes": float(total_mes),
            "total_mes_anterior": float(total_anterior),
            "variacao_absoluta": float(variacao_absoluta),
            "variacao_percentual": round(float(variacao_percentual), 2),
            "media_diaria": round(media_diaria, 2),
            "maior_gasto": maior_gasto,
            "quantidade_gastos": agg_atual['quantidade'] or 0,
            "ranking_categorias": ranking_categorias,
            "evolucao_mensal": evolucao_mensal,
            "total_receitas": float(total_receitas),
            "total_gastos_pagos": float(total_gastos_pagos),
            "total_a_pagar": float(total_a_pagar),
            "quantidade_pendentes": quantidade_pendentes,
            "saldo": float(saldo),
            "saldo_projetado": float(saldo_projetado),
            "previsao_mensagem": previsao_mensagem,
            "metas": metas_context
        })

    except Exception as e:
        logger.error(f"Erro no dashboard: {e}")
        return Response(
            {"erro": "Erro interno no servidor"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# -------------------------
# RECEITAS
# -------------------------
@api_view(['GET', 'POST'])
def receitas(request):
    try:
        if request.method == 'GET':
            user_family = get_user_family(request.user)

            if user_family:
                queryset = Receita.objects.filter(
                    Q(family=user_family) | Q(user=request.user, family__isnull=True)
                )
            else:
                queryset = Receita.objects.filter(user=request.user)

            # Filtro por período
            data_inicio = request.query_params.get('data_inicio')
            data_fim = request.query_params.get('data_fim')
            if data_inicio:
                queryset = queryset.filter(data__gte=data_inicio)
            if data_fim:
                queryset = queryset.filter(data__lte=data_fim)

            queryset = queryset.order_by('-data', '-criado_em')

            # Paginação simples
            limite = int(request.query_params.get('limite', 50))
            if limite > 100:
                limite = 100
            queryset = queryset[:limite]

            serializer = ReceitaSerializer(queryset, many=True)
            return Response({
                "receitas": serializer.data,
                "total": len(serializer.data)
            })

        elif request.method == 'POST':
            dados = request.data.copy()
            serializer = ReceitaSerializer(data=dados)

            if serializer.is_valid():
                family = get_user_family(request.user)
                receita = serializer.save(user=request.user, family=family)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )

            # Formatar erros de validação
            errors = {}
            for field, messages in serializer.errors.items():
                errors[field] = messages[0] if isinstance(messages, list) else str(messages)


    except Exception as e:
        logger.error(f"Erro na API de receitas: {e}")
        return Response(
            {"erro": "Erro interno no servidor"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# -------------------------
# EXPORTAÇÃO CSV / XLSX
# -------------------------
import csv
import io
from django.http import StreamingHttpResponse, HttpResponse

try:
    from openpyxl import Workbook
    _HAS_OPENPYXL = True
except ImportError:
    _HAS_OPENPYXL = False


def _get_gastos_filtrados(request):
    """Retorna queryset de gastos do usuário/família com os mesmos filtros de /api/gastos/."""
    queryset = get_user_gastos_queryset(request.user)

    categoria = request.query_params.get('categoria')
    if categoria:
        queryset = queryset.filter(categoria=categoria)

    data_inicio = request.query_params.get('data_inicio')
    data_fim = request.query_params.get('data_fim')
    if data_inicio:
        queryset = queryset.filter(data_efetiva__gte=data_inicio)
    if data_fim:
        queryset = queryset.filter(data_efetiva__lte=data_fim)

    competencia_inicio = request.query_params.get('competencia_inicio')
    competencia_fim = request.query_params.get('competencia_fim')
    if competencia_inicio:
        queryset = queryset.filter(data_competencia__gte=competencia_inicio)
    if competencia_fim:
        queryset = queryset.filter(data_competencia__lte=competencia_fim)

    pagamento_inicio = request.query_params.get('pagamento_inicio')
    pagamento_fim = request.query_params.get('pagamento_fim')
    if pagamento_inicio:
        queryset = queryset.filter(data_pagamento__gte=pagamento_inicio)
    if pagamento_fim:
        queryset = queryset.filter(data_pagamento__lte=pagamento_fim)

    pago = request.query_params.get('pago')
    if pago is not None:
        queryset = queryset.filter(pago=pago.lower() in ('true', '1', 'yes', 'sim'))

    return queryset.order_by('-data_efetiva', '-criado_em')


@api_view(['GET'])
def exportar_csv(request):
    try:
        queryset = _get_gastos_filtrados(request)

        def stream_csv():
            buffer = io.StringIO()
            writer = csv.writer(buffer)
            writer.writerow(['data', 'categoria', 'valor', 'descricao', 'pago', 'data_competencia', 'data_pagamento', 'criado_por'])
            yield buffer.getvalue()
            buffer.seek(0)
            buffer.truncate(0)

            for g in queryset.iterator():
                writer.writerow([
                    g.data,
                    g.get_categoria_display(),
                    str(g.valor).replace('.', ','),
                    g.descricao or '',
                    'Sim' if g.pago else 'Não',
                    g.data_competencia or '',
                    g.data_pagamento or '',
                    g.user.username
                ])
                yield buffer.getvalue()
                buffer.seek(0)
                buffer.truncate(0)

        response = StreamingHttpResponse(stream_csv(), content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="gastos.csv"'
        return response

    except Exception as e:
        logger.error(f"Erro na exportação CSV: {e}")
        return Response(
            {"erro": "Erro interno no servidor"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def exportar_xlsx(request):
    try:
        if not _HAS_OPENPYXL:
            return Response(
                {"erro": "Biblioteca openpyxl não instalada. Contate o administrador."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        queryset = _get_gastos_filtrados(request)

        wb = Workbook()
        ws = wb.active
        ws.title = "Gastos"

        headers = ['Data', 'Categoria', 'Valor', 'Descrição', 'Pago', 'Mês Competência', 'Data Pagamento', 'Criado por']
        ws.append(headers)

        for g in queryset.iterator():
            ws.append([
                g.data,
                g.get_categoria_display(),
                float(g.valor),
                g.descricao or '',
                'Sim' if g.pago else 'Não',
                g.data_competencia or '',
                g.data_pagamento or '',
                g.user.username
            ])

        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        logger.error(f"Erro na exportação XLSX: {e}")
        return Response(
            {"erro": "Erro interno no servidor"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# -------------------------
# METAS DE GASTO (Budget Goals)
# -------------------------

def _get_meta_status(pct):
    if pct > 100:
        return 'critical'
    elif pct > 80:
        return 'danger'
    elif pct > 50:
        return 'warning'
    return 'ok'


def _get_gasto_realizado(user, categoria, mes, ano):
    """Calcula o total gasto pelo usuário em uma categoria/mês/ano."""
    gastos = Gasto.objects.filter(
        user=user,
        data_competencia__month=mes,
        data_competencia__year=ano
    )
    if categoria:
        gastos = gastos.filter(categoria=categoria)
    total = gastos.aggregate(total=Sum('valor'))['total'] or 0
    return round(float(total), 2)


@api_view(['GET'])
def listar_metas(request):
    """Lista todas as metas do usuário para um mês/ano."""
    try:
        mes = int(request.query_params.get('mes', 0))
        ano = int(request.query_params.get('ano', 0))
        if not (1 <= mes <= 12 and ano > 2000):
            return Response(
                {"erro": "Mês (1-12) e ano (>2000) são obrigatórios"},
                status=status.HTTP_400_BAD_REQUEST
            )

        metas = MetaGasto.objects.filter(user=request.user, mes=mes, ano=ano)
        serializer = MetaGastoSerializer(metas, many=True)
        return Response({"metas": serializer.data, "mes": mes, "ano": ano})
    except Exception as e:
        logger.error(f"Erro ao listar metas: {e}")
        return Response(
            {"erro": "Erro interno no servidor"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def criar_meta(request):
    """Cria uma nova meta de gasto."""
    try:
        categoria = request.data.get('categoria') or None
        mes = int(request.data.get('mes', 0))
        ano = int(request.data.get('ano', 0))
        valor_meta = float(request.data.get('valor_meta', 0))

        if not (1 <= mes <= 12 and ano > 2000):
            return Response(
                {"erro": "Mês (1-12) e ano (>2000) são obrigatórios"},
                status=status.HTTP_400_BAD_REQUEST
            )
        if valor_meta <= 0:
            return Response(
                {"erro": "Valor da meta deve ser maior que zero"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verificar duplicata
        if MetaGasto.objects.filter(user=request.user, categoria=categoria, mes=mes, ano=ano).exists():
            return Response(
                {"erro": "Já existe uma meta para esta categoria neste período"},
                status=status.HTTP_400_BAD_REQUEST
            )

        meta = MetaGasto.objects.create(
            user=request.user,
            categoria=categoria,
            mes=mes,
            ano=ano,
            valor_meta=valor_meta
        )
        serializer = MetaGastoSerializer(meta)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Exception as e:
        logger.error(f"Erro ao criar meta: {e}")
        return Response(
            {"erro": "Erro interno no servidor"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PUT'])
def atualizar_meta(request, pk):
    """Atualiza o valor de uma meta existente."""
    try:
        meta = MetaGasto.objects.get(pk=pk, user=request.user)
        valor_meta = float(request.data.get('valor_meta', 0))

        if valor_meta <= 0:
            return Response(
                {"erro": "Valor da meta deve ser maior que zero"},
                status=status.HTTP_400_BAD_REQUEST
            )

        meta.valor_meta = valor_meta
        meta.save()
        serializer = MetaGastoSerializer(meta)
        return Response(serializer.data)
    except MetaGasto.DoesNotExist:
        return Response(
            {"erro": "Meta não encontrada"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Erro ao atualizar meta: {e}")
        return Response(
            {"erro": "Erro interno no servidor"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
def deletar_meta(request, pk):
    """Deleta uma meta de gasto."""
    try:
        meta = MetaGasto.objects.get(pk=pk, user=request.user)
        meta.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except MetaGasto.DoesNotExist:
        return Response(
            {"erro": "Meta não encontrada"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Erro ao deletar meta: {e}")
        return Response(
            {"erro": "Erro interno no servidor"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def _build_metas_context(user, mes, ano):
    """Constrói o contexto de metas para o dashboard."""
    metas = MetaGasto.objects.filter(user=user, mes=mes, ano=ano)
    
    geral = None
    por_categoria = []
    
    for meta in metas:
        serializer = MetaGastoSerializer(meta)
        data = serializer.data
        if meta.categoria is None:
            geral = data
        else:
            por_categoria.append(data)
    
    return {"geral": geral, "por_categoria": por_categoria}