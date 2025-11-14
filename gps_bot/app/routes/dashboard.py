"""
Rotas do Dashboard SLA
"""
from flask import Blueprint, render_template, request, jsonify
from app import cache
from app.models.dashboard import (
    buscar_resumo_tarefas, buscar_tarefas_por_dia_mes,
    buscar_heatmap_realizacao, buscar_heatmap_por_dia, buscar_top_executores,
    buscar_top_locais, buscar_distribuicao_status,
    buscar_opcoes_filtros
)
from datetime import datetime, timedelta
import calendar
import hashlib
import json

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


def extrair_filtros_request():
    """Extrai filtros dos parâmetros da requisição"""
    filtros = {}
    
    if request.args.get('cr'):
        filtros['cr'] = request.args.get('cr')
    
    if request.args.get('cliente'):
        filtros['cliente'] = request.args.get('cliente')
    
    if request.args.get('diretor_executivo'):
        filtros['diretor_executivo'] = request.args.get('diretor_executivo')
    
    if request.args.get('diretor_regional'):
        filtros['diretor_regional'] = request.args.get('diretor_regional')
    
    if request.args.get('gerente_regional'):
        filtros['gerente_regional'] = request.args.get('gerente_regional')
    
    if request.args.get('gerente'):
        filtros['gerente'] = request.args.get('gerente')
    
    if request.args.get('supervisor'):
        filtros['supervisor'] = request.args.get('supervisor')
    
    if request.args.get('pec_01'):
        filtros['pec_01'] = request.args.get('pec_01')
    
    if request.args.get('pec_02'):
        filtros['pec_02'] = request.args.get('pec_02')
    
    return filtros


def obter_periodo_mes_atual():
    """Retorna primeiro e último dia do mês atual"""
    hoje = datetime.now()
    primeiro_dia = datetime(hoje.year, hoje.month, 1)
    ultimo_dia_numero = calendar.monthrange(hoje.year, hoje.month)[1]
    ultimo_dia = datetime(hoje.year, hoje.month, ultimo_dia_numero, 23, 59, 59)
    
    return primeiro_dia, ultimo_dia


def get_cache_timeout():
    """
    Retorna timeout do cache baseado no mês:
    - Mês atual: 300s (5 minutos)
    - Meses passados: 86400s (24 horas)
    """
    mes = int(request.args.get('mes', datetime.now().month))
    ano = int(request.args.get('ano', datetime.now().year))
    
    hoje = datetime.now()
    eh_mes_atual = (mes == hoje.month and ano == hoje.year)
    
    return 300 if eh_mes_atual else 86400


def make_cache_key():
    """
    Cria chave de cache única baseada na URL completa e query string
    """
    query_string = request.query_string.decode('utf-8')
    cache_key = f"{request.path}?{query_string}"
    return hashlib.md5(cache_key.encode('utf-8')).hexdigest()


@bp.route('/')
def index():
    """Página principal do dashboard"""
    # Busca opções de filtros para popular os selects
    opcoes_filtros = buscar_opcoes_filtros()
    
    return render_template('dashboard/index.html', filtros_valores=opcoes_filtros)


@bp.route('/api/resumo')
@cache.cached(timeout=get_cache_timeout, make_cache_key=make_cache_key)
def api_resumo():
    """
    API: Retorna resumo com totais de tarefas (cards)
    GET /dashboard/api/resumo?cr=123&mes=11&ano=2024
    """
    try:
        filtros = extrair_filtros_request()
        
        # Período: mês/ano ou padrão (mês atual)
        mes = int(request.args.get('mes', datetime.now().month))
        ano = int(request.args.get('ano', datetime.now().year))
        
        primeiro_dia = datetime(ano, mes, 1)
        ultimo_dia_numero = calendar.monthrange(ano, mes)[1]
        ultimo_dia = datetime(ano, mes, ultimo_dia_numero, 23, 59, 59)
        
        stats = buscar_resumo_tarefas(filtros, primeiro_dia, ultimo_dia)
        
        return jsonify({
            'success': True,
            'data': stats,
            'periodo': {
                'mes': mes,
                'ano': ano,
                'mes_nome': calendar.month_name[mes]
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/api/tarefas-mes')
@cache.cached(timeout=get_cache_timeout, make_cache_key=make_cache_key)
def api_tarefas_mes():
    """
    API: Retorna tarefas agrupadas por dia do mês (gráfico de colunas)
    GET /dashboard/api/tarefas-mes?mes=11&ano=2024
    """
    try:
        filtros = extrair_filtros_request()
        
        mes = int(request.args.get('mes', datetime.now().month))
        ano = int(request.args.get('ano', datetime.now().year))
        
        dados = buscar_tarefas_por_dia_mes(filtros, mes, ano)
        
        return jsonify({
            'success': True,
            'data': dados
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/api/heatmap')
@cache.cached(timeout=get_cache_timeout, make_cache_key=make_cache_key)
def api_heatmap():
    """
    API: Retorna heatmap de realização por CR
    GET /dashboard/api/heatmap?mes=11&ano=2024
    """
    try:
        filtros = extrair_filtros_request()
        
        mes = int(request.args.get('mes', datetime.now().month))
        ano = int(request.args.get('ano', datetime.now().year))
        
        primeiro_dia = datetime(ano, mes, 1)
        ultimo_dia_numero = calendar.monthrange(ano, mes)[1]
        ultimo_dia = datetime(ano, mes, ultimo_dia_numero, 23, 59, 59)
        
        dados = buscar_heatmap_realizacao(filtros, primeiro_dia, ultimo_dia)
        
        return jsonify({
            'success': True,
            'data': dados
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/api/executores')
@cache.cached(timeout=get_cache_timeout, make_cache_key=make_cache_key)
def api_executores():
    """
    API: Retorna TOP executores
    GET /dashboard/api/executores?limit=10&mes=11&ano=2024
    """
    try:
        filtros = extrair_filtros_request()
        
        limit = int(request.args.get('limit', 10))
        mes = int(request.args.get('mes', datetime.now().month))
        ano = int(request.args.get('ano', datetime.now().year))
        
        primeiro_dia = datetime(ano, mes, 1)
        ultimo_dia_numero = calendar.monthrange(ano, mes)[1]
        ultimo_dia = datetime(ano, mes, ultimo_dia_numero, 23, 59, 59)
        
        dados = buscar_top_executores(filtros, primeiro_dia, ultimo_dia, limit)
        
        return jsonify({
            'success': True,
            'data': dados
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/api/locais')
@cache.cached(timeout=get_cache_timeout, make_cache_key=make_cache_key)
def api_locais():
    """
    API: Retorna TOP locais
    GET /dashboard/api/locais?limit=10&mes=11&ano=2024
    """
    try:
        filtros = extrair_filtros_request()
        
        limit = int(request.args.get('limit', 10))
        mes = int(request.args.get('mes', datetime.now().month))
        ano = int(request.args.get('ano', datetime.now().year))
        
        primeiro_dia = datetime(ano, mes, 1)
        ultimo_dia_numero = calendar.monthrange(ano, mes)[1]
        ultimo_dia = datetime(ano, mes, ultimo_dia_numero, 23, 59, 59)
        
        dados = buscar_top_locais(filtros, primeiro_dia, ultimo_dia, limit)
        
        return jsonify({
            'success': True,
            'data': dados
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/api/pizza')
@cache.cached(timeout=get_cache_timeout, make_cache_key=make_cache_key)
def api_pizza():
    """
    API: Retorna distribuição por status (gráfico de pizza)
    GET /dashboard/api/pizza?mes=11&ano=2024
    """
    try:
        filtros = extrair_filtros_request()
        
        mes = int(request.args.get('mes', datetime.now().month))
        ano = int(request.args.get('ano', datetime.now().year))
        
        primeiro_dia = datetime(ano, mes, 1)
        ultimo_dia_numero = calendar.monthrange(ano, mes)[1]
        ultimo_dia = datetime(ano, mes, ultimo_dia_numero, 23, 59, 59)
        
        dados = buscar_distribuicao_status(filtros, primeiro_dia, ultimo_dia)
        
        return jsonify({
            'success': True,
            'data': dados
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/api/filtros')
def api_filtros():
    """
    API: Retorna opções para os filtros
    GET /dashboard/api/filtros
    """
    try:
        opcoes = buscar_opcoes_filtros()
        
        return jsonify({
            'success': True,
            'data': opcoes
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/api/heatmap-dias')
@cache.cached(timeout=get_cache_timeout, make_cache_key=make_cache_key)
def api_heatmap_dias():
    """
    API: Retorna heatmap com CR x Dias do Mês
    GET /dashboard/api/heatmap-dias?mes=11&ano=2024
    """
    try:
        filtros = extrair_filtros_request()
        
        mes = int(request.args.get('mes', datetime.now().month))
        ano = int(request.args.get('ano', datetime.now().year))
        
        dados = buscar_heatmap_por_dia(filtros, mes, ano)
        
        return jsonify({
            'success': True,
            'data': dados,
            'mes': mes,
            'ano': ano
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

