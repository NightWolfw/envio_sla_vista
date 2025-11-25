"""
Scheduler para envios automatizados de SLA
"""
import atexit
import logging
import os
import threading
from pathlib import Path
from typing import Any, Dict
from urllib.parse import quote

import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta

import config as project_config
from app.models.agendamento import AGENDAMENTO_COLUMNS, listar_agendamentos, atualizar_agendamento, obter_agendamento
from app.models.grupo import obter_grupo, GRUPO_COLUMNS
from app.services.mensagem_agendamento import (
    calcular_datas_consulta,
    formatar_mensagem_programadas,
    formatar_mensagem_resultados,
)
from app.services.pdf_sla import gerar_pdf_relatorio
from app.services.sla_consulta import buscar_tarefas_por_periodo, buscar_tarefas_detalhadas
from app.services.dashboard_cache import get_cached_dashboard
from app.services.dashboard_refresh import atualizar_dashboard_cache
from app.models.dashboard_config import obter_config_dashboard
from app.services.whatsapp import enviar_mensagem_texto, enviar_pdf_whatsapp
logger = logging.getLogger(__name__)
TIMEZONE_BRASILIA = pytz.timezone('America/Sao_Paulo')
PUBLIC_BASE_URL = project_config.PUBLIC_API_BASE_URL.rstrip('/')

scheduler = BackgroundScheduler(timezone=TIMEZONE_BRASILIA)
ultimos_envios: Dict[str, bool] = {}  # Cache em memória para evitar duplicação
_scheduler_started = False
_dashboard_refresh_running = False

BASE_DIR = Path(__file__).resolve().parents[3]
LOCKFILE_PATH = Path(os.getenv("SCHEDULER_LOCKFILE", BASE_DIR / 'scheduler.lock'))


def _pdf_download_url(caminho_pdf: str) -> str:
    filename = Path(caminho_pdf).name
    return f"{PUBLIC_BASE_URL}/api/files/sla/{quote(filename)}"


def _agendar_remocao_pdf(caminho_pdf: str, delay: int = 300) -> None:
    def _remover():
        try:
            if os.path.exists(caminho_pdf):
                os.remove(caminho_pdf)
                logger.info(f"[PID {os.getpid()}] PDF temporário removido: {caminho_pdf}")
        except Exception as exc:
            logger.error(f"[PID {os.getpid()}] Erro ao remover PDF temporário {caminho_pdf}: {exc}")

    timer = threading.Timer(delay, _remover)
    timer.daemon = True
    timer.start()


def _normalizar_data_envio(data_envio: datetime) -> datetime:
    if data_envio.tzinfo is None:
        return TIMEZONE_BRASILIA.localize(data_envio)
    return data_envio.astimezone(TIMEZONE_BRASILIA)


def _obter_relatorio_contexto(agendamento: Dict[str, Any], cr: Any):
    data_envio_local = _normalizar_data_envio(agendamento['data_envio'])

    data_inicio, data_fim = calcular_datas_consulta(
        data_envio_local,
        agendamento['hora_inicio'],
        agendamento['dia_offset_inicio'],
        agendamento['hora_fim'],
        agendamento['dia_offset_fim']
    )

    meta_detalhes = None
    meta_stats = None

    if agendamento['tipo_envio'] == 'programadas':
        tarefas, meta_detalhes = buscar_tarefas_detalhadas(
            cr,
            data_inicio,
            data_fim,
            tipos_status=['em_aberto', 'iniciadas'],
            return_meta=True
        )
    else:
        tarefas, meta_detalhes = buscar_tarefas_detalhadas(
            cr,
            data_inicio,
            data_fim,
            return_meta=True
        )

    # Stats agregados
    stats, meta_stats = buscar_tarefas_por_periodo(
        cr,
        data_inicio,
        data_fim,
        agendamento['tipo_envio'],
        return_meta=True
    )

    return data_envio_local, data_inicio, data_fim, tarefas, stats, meta_detalhes, meta_stats


def gerar_pdf_agendamento(agendamento_id: int) -> str:
    registro = obter_agendamento(agendamento_id)
    if not registro:
        raise LookupError("Agendamento não encontrado")

    agendamento = dict(zip(AGENDAMENTO_COLUMNS, registro))
    grupo_row = obter_grupo(agendamento['grupo_id'])
    if not grupo_row:
        raise LookupError("Grupo não encontrado")

    grupo = dict(zip(GRUPO_COLUMNS, grupo_row))
    cr = grupo['cr']
    nome_grupo = grupo['nome_grupo']

    _, data_inicio, data_fim, tarefas, _, _, _ = _obter_relatorio_contexto(agendamento, cr)
    caminho_pdf = gerar_pdf_relatorio(cr, nome_grupo, tarefas, data_inicio, data_fim, agendamento['tipo_envio'])
    _agendar_remocao_pdf(caminho_pdf)
    return _pdf_download_url(caminho_pdf)


def cleanup_lockfile():
    """Remove lockfile ao fechar aplicação"""
    try:
        if LOCKFILE_PATH.exists():
            LOCKFILE_PATH.unlink()
            print(f"[UNLOCK] [PID {os.getpid()}] Lockfile removido automaticamente")
    except Exception as e:
        print(f"[PID {os.getpid()}] Erro ao remover lockfile no cleanup: {e}")


atexit.register(cleanup_lockfile)


def registrar_log_envio(agendamento_id, grupo_id, status, mensagem_enviada='', resposta_api='', erro=''):
    """Registra log de envio no banco"""
    try:
        from app.models.database import get_db_site
        conn = get_db_site()
        cur = conn.cursor()

        query = """
            INSERT INTO agendamento_logs 
            (agendamento_id, grupo_id, data_envio, status, mensagem_enviada, resposta_api, erro)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        cur.execute(query, (
            agendamento_id,
            grupo_id,
            datetime.now(TIMEZONE_BRASILIA),
            status,
            mensagem_enviada,
            resposta_api,
            erro
        ))

        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        logger.error(f"[PID {os.getpid()}] Erro ao registrar log: {e}")


def calcular_proximo_envio(data_envio_atual, dias_semana):
    """Calcula próxima data mantendo timezone de Brasília"""
    dia_semana_map = {
        'seg': 0, 'ter': 1, 'qua': 2, 'qui': 3,
        'sex': 4, 'sab': 5, 'dom': 6
    }

    dias_numeros = [dia_semana_map[dia.strip()] for dia in dias_semana.split(',')]
    dias_numeros.sort()

    # Garante que está em Brasília
    if data_envio_atual.tzinfo is None:
        data_atual = TIMEZONE_BRASILIA.localize(data_envio_atual)
    else:
        data_atual = data_envio_atual.astimezone(TIMEZONE_BRASILIA)

    proxima_data = data_atual + timedelta(days=1)

    for _ in range(7):
        if proxima_data.weekday() in dias_numeros:
            return proxima_data.replace(hour=data_atual.hour, minute=data_atual.minute, second=0, microsecond=0)
        proxima_data += timedelta(days=1)

    return data_atual


def atualizar_proximo_envio(agendamento_id, nova_data):
    """Atualiza próximo envio mantendo horário correto em Brasília"""
    try:
        from app.models.database import get_db_site
        conn = get_db_site()
        cur = conn.cursor()

        # Salva sem timezone (assume Brasília)
        if nova_data.tzinfo is not None:
            nova_data = nova_data.replace(tzinfo=None)

        query = """
            UPDATE agendamentos 
            SET data_envio = %s, atualizado_em = NOW()
            WHERE id = %s
        """

        cur.execute(query, (nova_data, agendamento_id))
        conn.commit()
        cur.close()
        conn.close()

        logger.info(f"[PID {os.getpid()}] Próximo envio atualizado para {nova_data.strftime('%d/%m/%Y %H:%M')}")
    except Exception as e:
        logger.error(f"[PID {os.getpid()}] Erro ao atualizar próximo envio: {e}")


def enviar_sla_agendado(agendamento, atualizar_proximo=True):
    """Executa o envio de SLA.

    Args:
        agendamento: registro completo do agendamento atual.
        atualizar_proximo: define se o próximo envio deve ser recalculado após a execução.
    """
    print(f"\n{'#' * 60}")
    print(f"[ENVIO] [PID {os.getpid()}] INICIANDO ENVIO - Agendamento {agendamento['id']}")
    print(f"{'#' * 60}\n")

    try:
        logger.info(f"[PID {os.getpid()}] === INICIANDO ENVIO PARA AGENDAMENTO {agendamento['id']} ===")

        grupo_row = obter_grupo(agendamento['grupo_id'])
        if not grupo_row:
            raise Exception("Grupo não encontrado")

        grupo = dict(zip(GRUPO_COLUMNS, grupo_row))
        group_id = grupo['group_id']
        cr = grupo['cr']
        nome_grupo = grupo['nome_grupo']
        envio_pdf_habilitado = bool(grupo.get('envio_pdf'))

        (
            data_envio_local,
            data_inicio,
            data_fim,
            tarefas,
            stats,
            meta_detalhes,
            meta_stats,
        ) = _obter_relatorio_contexto(agendamento, cr)

        # Formata mensagem
        if agendamento['tipo_envio'] == 'resultados':
            mensagem = formatar_mensagem_resultados(data_inicio, data_fim, stats, data_envio_local)
        else:
            mensagem = formatar_mensagem_programadas(data_inicio, data_fim, stats, data_envio_local)

        caminho_pdf = None
        pdf_resposta = None
        if envio_pdf_habilitado:
            logger.info(f"[PID {os.getpid()}] Gerando PDF para envio direto...")
            caminho_pdf = gerar_pdf_relatorio(
                cr, nome_grupo, tarefas, data_inicio, data_fim, agendamento['tipo_envio']
            )
            _agendar_remocao_pdf(caminho_pdf)
        else:
            logger.info(f"[PID {os.getpid()}] Envio de PDF desabilitado para este grupo.")

        logger.info(f"[PID {os.getpid()}] Enviando mensagem de texto...")
        resposta_msg = enviar_mensagem_texto(group_id, mensagem)

        pdf_erro = None
        if envio_pdf_habilitado and caminho_pdf:
            try:
                logger.info(f"[PID {os.getpid()}] Enviando PDF como anexo...")
                pdf_resposta = enviar_pdf_whatsapp(
                    group_id,
                    caminho_pdf,
                    caption=f"Relatório SLA - {nome_grupo}"
                )
            except Exception as exc:
                pdf_erro = str(exc)
                logger.error(f"[PID {os.getpid()}] Erro ao enviar PDF: {pdf_erro}")

        # Atualiza próximo envio quando necessário
        if atualizar_proximo:
            proxima_data = calcular_proximo_envio(agendamento['data_envio'], agendamento['dias_semana'])
            atualizar_proximo_envio(agendamento['id'], proxima_data)

        # Registra log
        contexto_envio = (
            f"periodo={data_inicio.isoformat()}->{data_fim.isoformat()} "
            f"tz=America/Sao_Paulo tarefas={len(tarefas)} stats={stats}"
        )
        resposta_api = (
            f"{contexto_envio} "
            f"| query_detalhes={meta_detalhes} "
            f"| query_stats={meta_stats} "
            f"| MSG: {resposta_msg}"
        )
        if pdf_resposta:
            resposta_api += f", PDF: {pdf_resposta}"

        status = 'sucesso' if not pdf_erro else 'erro_pdf'
        registrar_log_envio(
            agendamento['id'],
            agendamento['grupo_id'],
            status,
            mensagem,
            resposta_api,
            pdf_erro or ''
        )

        logger.info(f"[PID {os.getpid()}] === ENVIO CONCLUÍDO ===")

    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        logger.error(f"[PID {os.getpid()}] ERRO: {error_detail}")

        registrar_log_envio(
            agendamento.get('id', 0),
            agendamento.get('grupo_id', 0),
            'erro',
            '',
            '',
            error_detail
        )
        raise


def enviar_agendamento_imediato(agendamento_id: int):
    """Executa o envio manual de um agendamento sem alterar a agenda."""
    registro = obter_agendamento(agendamento_id)
    if not registro:
        raise LookupError("Agendamento não encontrado")

    agendamento = dict(zip(AGENDAMENTO_COLUMNS, registro))
    if not agendamento.get('ativo'):
        raise ValueError("Agendamento está pausado.")

    enviar_sla_agendado(agendamento, atualizar_proximo=False)
    return agendamento


def verificar_agendamentos():
    """Verifica agendamentos (COM PROTEÇÃO ANTI-DUPLICAÇÃO)"""
    try:
        agora = datetime.now(TIMEZONE_BRASILIA)
        chave_minuto = agora.strftime('%Y-%m-%d %H:%M')

        print(f"\n{'=' * 60}")
        print(f"[CHECK] [PID {os.getpid()}] VERIFICANDO AGENDAMENTOS EM {chave_minuto} (Brasília)")
        print(f"{'=' * 60}")

        agendamentos = listar_agendamentos()
        print(f"[INFO] [PID {os.getpid()}] Total de agendamentos: {len(agendamentos)}")
        print(f"[CACHE] [PID {os.getpid()}] Cache atual: {list(ultimos_envios.keys())}")

        dia_semana_map = {0: 'seg', 1: 'ter', 2: 'qua', 3: 'qui', 4: 'sex', 5: 'sab', 6: 'dom'}
        dia_atual = dia_semana_map[agora.weekday()]
        print(f"[DIA] [PID {os.getpid()}] Dia atual: {dia_atual}")

        for agendamento in agendamentos:
            print(f"\n[PID {os.getpid()}] --- Analisando agendamento {agendamento['id']} ---")
            print(f"[PID {os.getpid()}] Ativo: {agendamento['ativo']}")
            print(f"[PID {os.getpid()}] Dias: {agendamento['dias_semana']}")
            print(f"[PID {os.getpid()}] Hora agendada: {agendamento['data_envio'].strftime('%H:%M')}")
            print(f"[PID {os.getpid()}] Hora atual: {agora.strftime('%H:%M')}")

            if not agendamento['ativo']:
                print(f"[PID {os.getpid()}] [SKIP] INATIVO - pulando")
                continue

            dias_envio = agendamento['dias_semana'].split(',')
            if dia_atual not in dias_envio:
                print(f"[PID {os.getpid()}] [SKIP] Hoje ({dia_atual}) não está nos dias {dias_envio} - pulando")
                continue

            data_envio = agendamento['data_envio']

            chave_agendamento = f"{agendamento['id']}_{chave_minuto}"
            print(f"[PID {os.getpid()}] [KEY] Chave: {chave_agendamento}")

            if chave_agendamento in ultimos_envios:
                print(f"[PID {os.getpid()}] [WARN] JÁ ENVIADO NESTE_MINUTO - IGNORANDO")
                continue

            if agora.hour == data_envio.hour and agora.minute == data_envio.minute:
                print(f"[PID {os.getpid()}] [OK] HORÁRIO BATEU! Executando envio...")
                print(f"[PID {os.getpid()}] [RUN] EXECUTANDO AGENDAMENTO {agendamento['id']}")

                ultimos_envios[chave_agendamento] = True
                print(f"[PID {os.getpid()}] [LOCK] Marcado no cache: {chave_agendamento}")

                limite = (agora - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M')
                chaves_antigas = [k for k in list(ultimos_envios.keys()) if k.split('_', 1)[1] < limite]
                for k in chaves_antigas:
                    del ultimos_envios[k]

                enviar_sla_agendado(agendamento)
            else:
                print(f"[PID {os.getpid()}] [WAIT] Horário não bateu: {agora.hour}:{agora.minute} != {data_envio.hour}:{data_envio.minute}")

        print(f"\n{'=' * 60}\n")

    except Exception as e:
        import traceback
        print(f"[PID {os.getpid()}] [ERROR] ERRO NA VERIFICAÇÃO:")
        print(traceback.format_exc())
        logger.error(f"[PID {os.getpid()}] Erro: {traceback.format_exc()}")


def _refresh_dashboard_cache_if_needed():
    """
    Atualiza cache do dashboard conforme intervalo configurado.
    Reintenta a cada execução do scheduler (minuto) verificando janela de horário.
    """
    global _dashboard_refresh_running
    if _dashboard_refresh_running:
        return
    _dashboard_refresh_running = True
    try:
        cfg = obter_config_dashboard()
        agora = datetime.now(TIMEZONE_BRASILIA)
        inicio = datetime.combine(agora.date(), cfg["hora_inicio"]).replace(tzinfo=TIMEZONE_BRASILIA)
        fim = datetime.combine(agora.date(), cfg["hora_fim"]).replace(tzinfo=TIMEZONE_BRASILIA)

        if not (inicio <= agora <= fim):
            return

        cached = get_cached_dashboard({})
        last = None
        if cached and cached.get("last_updated"):
            try:
                last = datetime.fromisoformat(cached["last_updated"])
            except Exception:
                last = None

        delta_ok = False
        if last:
            delta = agora - last.astimezone(TIMEZONE_BRASILIA)
            delta_ok = delta.total_seconds() >= cfg["intervalo_minutos"] * 60
        else:
            delta_ok = True

        if delta_ok:
            logger.info(f"[Dashboard] Atualizando cache (intervalo {cfg['intervalo_minutos']} min).")
            from app.services.dashboard_etl import carregar_mes_corrente
            carregar_mes_corrente({})
            atualizar_dashboard_cache({})
    except Exception as exc:
        logger.error(f"[Dashboard] Falha ao atualizar cache: {exc}")
    finally:
        _dashboard_refresh_running = False


def iniciar_scheduler():
    """Inicia scheduler COM PROTEÇÃO ANTI-DUPLICAÇÃO (LOCKFILE)"""
    global _scheduler_started

    if _scheduler_started:
        return
    _scheduler_started = True

    print(f"\n{'=' * 60}")
    print(f"[PID {os.getpid()}] TENTANDO INICIAR SCHEDULER")
    print(f"{'=' * 60}\n")

    # ✅ Verificar se o processo do lockfile ainda existe
    if LOCKFILE_PATH.exists():
        try:
            with LOCKFILE_PATH.open('r') as f:
                old_pid = int(f.read().strip())

            print(f"[PID {os.getpid()}] 🔍 Lockfile encontrado com PID: {old_pid}")

            # Verifica se o processo ainda existe
            try:
                os.kill(old_pid, 0)  # Não mata, só verifica
                print(f"[PID {os.getpid()}] ⚠️ SCHEDULER JÁ INICIADO NO PID {old_pid}. Não iniciando de novo.")
                logger.warning(f"Scheduler já está rodando no PID {old_pid}")
                return
            except OSError:
                # Processo não existe mais, pode remover o lockfile
                print(f"[PID {os.getpid()}] 🧹 Lockfile órfão detectado (PID {old_pid} não existe). Removendo...")
                LOCKFILE_PATH.unlink()
        except Exception as e:
            print(f"[PID {os.getpid()}] ⚠️ Erro ao verificar lockfile: {e}. Removendo...")
            LOCKFILE_PATH.unlink()

    try:
        LOCKFILE_PATH.write_text(str(os.getpid()))
        print(f"[PID {os.getpid()}] [LOCK] Lockfile criado: {LOCKFILE_PATH}")
    except Exception as e:
        print(f"[PID {os.getpid()}] [ERROR] Erro ao criar lockfile: {e}")
        logger.error(f"Erro ao criar lockfile: {e}")
        return

    if not scheduler.running:
        scheduler.add_job(
            verificar_agendamentos,
            CronTrigger(minute='*', timezone=TIMEZONE_BRASILIA),
            id='verificar_agendamentos',
            replace_existing=True
        )
        scheduler.add_job(
            _refresh_dashboard_cache_if_needed,
            CronTrigger(minute='*', timezone=TIMEZONE_BRASILIA),
            id='atualizar_dashboard_cache',
            replace_existing=True
        )
        scheduler.start()
        print(f"[PID {os.getpid()}] [SUCCESS] Scheduler iniciado com sucesso!")
        logger.info(f"[PID {os.getpid()}] Scheduler iniciado com sucesso!")
    else:
        print(f"[PID {os.getpid()}] [WARN] Scheduler já estava rodando!")


def parar_scheduler():
    """Para scheduler E remove lockfile"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info(f"[PID {os.getpid()}] Scheduler parado")

    cleanup_lockfile()
    global _scheduler_started
    _scheduler_started = False
