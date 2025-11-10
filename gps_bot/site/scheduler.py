import time
import psycopg2
import requests
from datetime import datetime, date
import sys
import os

# Adiciona o diretório pai ao path para importar o config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


def conectar_bd():
    """Conecta ao banco de dados do site admin"""
    return psycopg2.connect(
        dbname=config.DB_SITE_CONFIG['database'],
        user=config.DB_SITE_CONFIG['user'],
        password=config.DB_SITE_CONFIG['password'],
        host=config.DB_SITE_CONFIG['host'],
        port=config.DB_SITE_CONFIG['port']
    )


def obter_grupos_para_envio(grupos_selecionados):
    """Retorna lista de grupos que devem receber a mensagem"""
    conn = conectar_bd()
    cur = conn.cursor()

    if grupos_selecionados and grupos_selecionados[0] == 'TODOS':
        cur.execute("SELECT group_id, nome_grupo FROM grupos_whatsapp WHERE envio = true")
    else:
        placeholders = ','.join(['%s'] * len(grupos_selecionados))
        cur.execute(
            f"SELECT group_id, nome_grupo FROM grupos_whatsapp WHERE group_id IN ({placeholders}) AND envio = true",
            grupos_selecionados)

    grupos = cur.fetchall()
    cur.close()
    conn.close()
    return grupos


def registrar_envio(mensagem_agendada_id, group_id, nome_grupo, mensagem, status, erro_detalhe=None):
    """Registra um envio no log"""
    conn = conectar_bd()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO log_envios 
        (mensagem_agendada_id, group_id, nome_grupo, mensagem, status, erro_detalhe)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (mensagem_agendada_id, group_id, nome_grupo, mensagem, status, erro_detalhe))

    conn.commit()
    cur.close()
    conn.close()


def enviar_mensagem_whatsapp(group_id, mensagem):
    """Envia mensagem via Evolution API"""
    url = f"{config.EVOLUTION_CONFIG['url']}/message/sendText/{config.EVOLUTION_CONFIG['instance']}"

    headers = {
        'Content-Type': 'application/json',
        'apikey': config.EVOLUTION_CONFIG['apikey']
    }

    payload = {
        'number': group_id,
        'text': mensagem
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        return True, None
    except requests.exceptions.RequestException as e:
        return False, str(e)


def verificar_e_enviar_mensagens():
    """Verifica mensagens agendadas e envia no horário correto"""
    conn = conectar_bd()
    cur = conn.cursor()

    agora = datetime.now()
    hora_atual = agora.strftime('%H:%M')
    data_atual = agora.date()
    dia_semana_atual = agora.weekday()  # 0=Segunda, 6=Domingo
    # Ajusta para domingo=0
    dia_semana_atual = 0 if dia_semana_atual == 6 else dia_semana_atual + 1

    print(f"[{agora.strftime('%Y-%m-%d %H:%M:%S')}] Verificando mensagens agendadas...")

    # Busca mensagens ativas que devem ser enviadas agora
    cur.execute("""
        SELECT * FROM mensagens_agendadas 
        WHERE ativo = true 
        AND horario = %s
        AND data_inicio <= %s
        AND (data_fim IS NULL OR data_fim >= %s)
    """, (hora_atual, data_atual, data_atual))

    mensagens = cur.fetchall()

    for msg in mensagens:
        msg_id = msg[0]
        mensagem_texto = msg[1]
        grupos_selecionados = msg[2]
        tipo_recorrencia = msg[3]
        dias_semana = msg[4]

        # Verifica se deve enviar hoje
        deve_enviar = False

        if tipo_recorrencia == 'UNICO':
            # Envio único: só envia na data de início
            if data_atual == msg[6]:
                deve_enviar = True
                # Desativa após enviar
                cur.execute("UPDATE mensagens_agendadas SET ativo = false WHERE id = %s", (msg_id,))
                conn.commit()

        elif tipo_recorrencia == 'RECORRENTE':
            # Envio recorrente: verifica se hoje está nos dias da semana
            if dias_semana and dia_semana_atual in dias_semana:
                deve_enviar = True

        if deve_enviar:
            print(f"📨 Enviando mensagem #{msg_id}: {mensagem_texto[:50]}...")

            # Busca grupos para envio
            grupos = obter_grupos_para_envio(grupos_selecionados)

            for group_id, nome_grupo in grupos:
                print(f"  → Enviando para: {nome_grupo} ({group_id})")

                sucesso, erro = enviar_mensagem_whatsapp(group_id, mensagem_texto)

                if sucesso:
                    registrar_envio(msg_id, group_id, nome_grupo, mensagem_texto, 'SUCESSO')
                    print(f"    ✅ Enviado com sucesso!")
                else:
                    registrar_envio(msg_id, group_id, nome_grupo, mensagem_texto, 'ERRO', erro)
                    print(f"    ❌ Erro: {erro}")

                # Delay entre envios pra não sobrecarregar
                time.sleep(1)

    cur.close()
    conn.close()


def main():
    """Loop principal do scheduler"""
    print("🚀 Scheduler de mensagens iniciado!")
    print(f"Verificando a cada minuto...")

    while True:
        try:
            verificar_e_enviar_mensagens()
        except Exception as e:
            print(f"❌ Erro no scheduler: {e}")

        # Aguarda 60 segundos até a próxima verificação
        time.sleep(60)


if __name__ == '__main__':
    main()
