"""
Scheduler para envios automatizados de SLA
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
import pytz
import logging
import os

logger = logging.getLogger(__name__)
TIMEZONE_BRASILIA = pytz.timezone('America/Sao_Paulo')

scheduler = BackgroundScheduler(timezone=TIMEZONE_BRASILIA)
flask_app = None
ultimos_envios = {}  # Cache em memória para evitar duplicação


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
        logger.error(f"Erro ao registrar log: {e}")


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

        logger.info(f"Próximo envio atualizado para {nova_data.strftime('%d/%m/%Y %H:%M')}")
    except Exception as e:
        logger.error(f"Erro ao atualizar próximo envio: {e}")


def enviar_sla_agendado(agendamento):
    """Executa o envio de SLA"""
    print(f"\n{'#' * 60}")
    print(f"📤 INICIANDO ENVIO - Agendamento {agendamento['id']}")
    print(f"{'#' * 60}\n")

    try:
        with flask_app.app_context():
            from app.models.grupo import obter_grupo
            from app.services.sla_consulta import buscar_tarefas_por_periodo, buscar_tarefas_detalhadas
            from app.services.mensagem_agendamento import formatar_mensagem_resultados, formatar_mensagem_programadas, calcular_datas_consulta
            from app.services.pdf_sla import gerar_pdf_relatorio
            from app.services.whatsapp import enviar_mensagem_texto, enviar_pdf_whatsapp

            logger.info(f"=== INICIANDO ENVIO PARA AGENDAMENTO {agendamento['id']} ===")

            grupo = obter_grupo(agendamento['grupo_id'])
            if not grupo:
                raise Exception("Grupo não encontrado")

            group_id = grupo[1]
            cr = grupo[4]
            nome_grupo = grupo[2]

            # Calcula período
            data_envio = agendamento['data_envio']
            if data_envio.tzinfo is None:
                data_envio = TIMEZONE_BRASILIA.localize(data_envio)

            data_inicio, data_fim = calcular_datas_consulta(
                data_envio,
                agendamento['hora_inicio'],
                agendamento['dia_offset_inicio'],
                agendamento['hora_fim'],
                agendamento['dia_offset_fim']
            )

            # Busca stats
            stats = buscar_tarefas_por_periodo(cr, data_inicio, data_fim, agendamento['tipo_envio'])

            # Formata mensagem
            if agendamento['tipo_envio'] == 'resultados':
                mensagem = formatar_mensagem_resultados(data_inicio, data_fim, stats, data_envio)
            else:
                mensagem = formatar_mensagem_programadas(data_inicio, data_fim, stats, data_envio)

            # Envia mensagem
            logger.info(f"Enviando mensagem...")
            resposta_msg = enviar_mensagem_texto(group_id, mensagem)

            # Busca tarefas para PDF
            if agendamento['tipo_envio'] == 'programadas':
                tarefas = buscar_tarefas_detalhadas(cr, data_inicio, data_fim, tipos_status=['em_aberto', 'iniciadas'])
            else:
                tarefas = buscar_tarefas_detalhadas(cr, data_inicio, data_fim)

            # Gera e envia PDF
            logger.info(f"Gerando PDF...")
            caminho_pdf = gerar_pdf_relatorio(cr, nome_grupo, tarefas, data_inicio, data_fim, agendamento['tipo_envio'])

            logger.info(f"Enviando PDF...")
            resposta_pdf = enviar_pdf_whatsapp(group_id, caminho_pdf, f"Relatório SLA - {nome_grupo}")

            # Atualiza próximo envio
            proxima_data = calcular_proximo_envio(agendamento['data_envio'], agendamento['dias_semana'])
            atualizar_proximo_envio(agendamento['id'], proxima_data)

            # Registra log
            registrar_log_envio(
                agendamento['id'],
                agendamento['grupo_id'],
                'sucesso',
                mensagem,
                f"MSG: {resposta_msg}, PDF: {resposta_pdf}",
                ''
            )

            logger.info(f"=== ENVIO CONCLUÍDO ===")

    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        logger.error(f"ERRO: {error_detail}")

        registrar_log_envio(
            agendamento.get('id', 0),
            agendamento.get('grupo_id', 0),
            'erro',
            '',
            '',
            error_detail
        )
        raise


def verificar_agendamentos():
    """Verifica agendamentos (COM PROTEÇÃO ANTI-DUPLICAÇÃO)"""
    try:
        with flask_app.app_context():
            from app.models.agendamento import listar_agendamentos

            agora = datetime.now(TIMEZONE_BRASILIA)
            chave_minuto = agora.strftime('%Y-%m-%d %H:%M')

            print(f"\n{'=' * 60}")
            print(f"🔍 VERIFICANDO AGENDAMENTOS EM {chave_minuto} (Brasília)")
            print(f"{'=' * 60}")

            agendamentos = listar_agendamentos()
            print(f"📊 Total de agendamentos: {len(agendamentos)}")
            print(f"🔒 Cache atual: {list(ultimos_envios.keys())}")

            dia_semana_map = {0: 'seg', 1: 'ter', 2: 'qua', 3: 'qui', 4: 'sex', 5: 'sab', 6: 'dom'}
            dia_atual = dia_semana_map[agora.weekday()]
            print(f"📅 Dia atual: {dia_atual}")

            for agendamento in agendamentos:
                print(f"\n--- Analisando agendamento {agendamento['id']} ---")
                print(f"Ativo: {agendamento['ativo']}")
                print(f"Dias: {agendamento['dias_semana']}")
                print(f"Hora agendada: {agendamento['data_envio'].strftime('%H:%M')}")
                print(f"Hora atual: {agora.strftime('%H:%M')}")

                if not agendamento['ativo']:
                    print("❌ INATIVO - pulando")
                    continue

                dias_envio = agendamento['dias_semana'].split(',')
                if dia_atual not in dias_envio:
                    print(f"❌ Hoje ({dia_atual}) não está nos dias {dias_envio} - pulando")
                    continue

                # Lê data_envio COMO SE FOSSE Brasília
                data_envio = agendamento['data_envio']

                # PROTEÇÃO: Verifica se já enviou neste minuto
                chave_agendamento = f"{agendamento['id']}_{chave_minuto}"
                print(f"🔑 Chave: {chave_agendamento}")

                if chave_agendamento in ultimos_envios:
                    print(f"⚠️ JÁ ENVIADO NESTE_MINUTO - IGNORANDO")
                    continue

                # Verifica hora
                if agora.hour == data_envio.hour and agora.minute == data_envio.minute:
                    print(f"✅ HORÁRIO BATEU! Executando envio...")
                    print(f"🚀 EXECUTANDO AGENDAMENTO {agendamento['id']}")

                    # Marca como enviado ANTES de executar
                    ultimos_envios[chave_agendamento] = True
                    print(f"🔒 Marcado no cache: {chave_agendamento}")

                    # Limpa cache antigo
                    limite = (agora - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M')
                    chaves_antigas = [k for k in ultimos_envios.keys() if k.split('_', 1)[1] < limite]
                    for k in chaves_antigas:
                        del ultimos_envios[k]

                    enviar_sla_agendado(agendamento)
                else:
                    print(f"⏰ Horário não bateu: {agora.hour}:{agora.minute} != {data_envio.hour}:{data_envio.minute}")

            print(f"\n{'=' * 60}\n")

    except Exception as e:
        import traceback
        print(f"❌ ERRO NA VERIFICAÇÃO:")
        print(traceback.format_exc())
        logger.error(f"Erro: {traceback.format_exc()}")


def iniciar_scheduler(app):
    """Inicia scheduler COM PROTEÇÃO ANTI-DUPLICAÇÃO (LOCKFILE)"""
    global flask_app
    flask_app = app

    # LOCKFILE para evitar iniciar duas vezes
    LOCKFILE = os.path.join(os.getcwd(), 'scheduler.lock')
    if os.path.exists(LOCKFILE):
        print("⚠️ SCHEDULER JÁ INICIADO EM OUTRO PROCESSO. Não iniciando de novo.")
        logger.warning("Scheduler já está rodando em outro processo")
        return
    try:
        with open(LOCKFILE, 'w') as f:
            f.write(str(os.getpid()))
        print(f"🔒 Lockfile criado: {LOCKFILE}")
    except Exception as e:
        print(f"❌ Erro ao criar lockfile: {e}")
        logger.error(f"Erro ao criar lockfile: {e}")
        return

    if not scheduler.running:
        scheduler.add_job(
            verificar_agendamentos,
            CronTrigger(minute='*', timezone=TIMEZONE_BRASILIA),
            id='verificar_agendamentos',
            replace_existing=True
        )
        scheduler.start()
        print("✅ Scheduler iniciado com sucesso!")
        logger.info("Scheduler iniciado com sucesso!")


def parar_scheduler():
    """Para scheduler E remove lockfile"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler parado")

    # Remove lockfile
    LOCKFILE = os.path.join(os.getcwd(), 'scheduler.lock')
    try:
        if os.path.exists(LOCKFILE):
            os.remove(LOCKFILE)
            print(f"🔓 Lockfile removido: {LOCKFILE}")
    except Exception as e:
        logger.error(f"Erro ao remover lockfile: {e}")
