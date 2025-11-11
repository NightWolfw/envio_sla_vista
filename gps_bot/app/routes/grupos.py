from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.grupo import listar_grupos, obter_valores_unicos_filtros

bp = Blueprint('grupos', __name__, url_prefix='/grupos')

@bp.route('/')
def gerenciar():
    filtros_valores = obter_valores_unicos_filtros(apenas_ativos=False)
    filtro_id = request.args.get('filtro_id', '')
    filtro_cr = request.args.get('filtro_cr', '')
    filtro_nome = request.args.get('filtro_nome', '')
    filtros = {
        'diretor_executivo': request.args.get('diretor_executivo', ''),
        'diretor_regional': request.args.get('diretor_regional', ''),
        'gerente_regional': request.args.get('gerente_regional', ''),
        'gerente': request.args.get('gerente', ''),
        'supervisor': request.args.get('supervisor', ''),
        'cliente': request.args.get('cliente', ''),
        'pec_01': request.args.get('pec_01', ''),
        'pec_02': request.args.get('pec_02', ''),
        'cr': filtro_cr
    }
    filtros = {k: v for k, v in filtros.items() if v}
    grupos = listar_grupos(filtro_id, filtro_cr, filtro_nome, filtros if filtros else None)
    return render_template(
        'grupos/gerenciar.html',
        grupos=grupos,
        filtro_id=filtro_id,
        filtro_cr=filtro_cr,
        filtro_nome=filtro_nome,
        filtro_diretor_executivo=request.args.get('diretor_executivo', ''),
        filtro_diretor_regional=request.args.get('diretor_regional', ''),
        filtro_gerente_regional=request.args.get('gerente_regional', ''),
        filtro_gerente=request.args.get('gerente', ''),
        filtro_supervisor=request.args.get('supervisor', ''),
        filtro_cliente=request.args.get('cliente', ''),
        filtro_pec_01=request.args.get('pec_01', ''),
        filtro_pec_02=request.args.get('pec_02', ''),
        filtros_valores=filtros_valores
    )
