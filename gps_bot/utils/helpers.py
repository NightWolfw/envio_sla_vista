"""
Funções auxiliares gerais do sistema
"""
import re
from datetime import datetime, timedelta


def formatar_cr(cr_valor):
    """Formata CR com zeros à esquerda (5 dígitos)"""
    if cr_valor is None:
        return None

    try:
        # Remove espaços e zeros à esquerda primeiro
        cr_limpo = str(cr_valor).strip().lstrip('0')
        if not cr_limpo:
            cr_limpo = '0'

        # Converte para int e formata com 5 dígitos
        cr_int = int(float(cr_limpo))
        return f"{cr_int:05d}"
    except (ValueError, TypeError):
        return str(cr_valor)


def validar_group_id(group_id):
    """Valida formato de ID de grupo WhatsApp"""
    if not group_id:
        return False

    # Formato esperado: números@g.us ou números-números@g.us
    pattern = r'^\d+(-\d+)?@g\.us$'
    return bool(re.match(pattern, group_id))


def dias_semana_para_texto(dias_lista):
    """Converte lista de dias da semana em texto legível"""
    if not dias_lista:
        return "Nenhum dia selecionado"

    dias_nomes = {
        0: 'Segunda',
        1: 'Terça',
        2: 'Quarta',
        3: 'Quinta',
        4: 'Sexta',
        5: 'Sábado',
        6: 'Domingo'
    }

    dias_ordenados = sorted(dias_lista)
    return ', '.join([dias_nomes.get(d, str(d)) for d in dias_ordenados])


def formatar_horario(horario_str):
    """Formata string de horário para HH:MM"""
    try:
        if isinstance(horario_str, str):
            # Remove segundos se existir
            partes = horario_str.split(':')
            return f"{partes[0]:0>2}:{partes[1]:0>2}"
        return horario_str
    except:
        return horario_str


def calcular_proximo_envio(horario, dias_semana=None):
    """Calcula data/hora do próximo envio baseado em horário e dias da semana"""
    agora = datetime.now()
    hora, minuto = map(int, horario.split(':'))

    # Se não tem dias específicos, próximo envio é hoje ou amanhã
    if not dias_semana:
        proximo = agora.replace(hour=hora, minute=minuto, second=0, microsecond=0)
        if proximo <= agora:
            proximo += timedelta(days=1)
        return proximo

    # Procura próximo dia da semana válido
    for i in range(8):  # Máximo 7 dias à frente
        data_teste = agora + timedelta(days=i)
        if data_teste.weekday() in dias_semana:
            proximo = data_teste.replace(hour=hora, minute=minuto, second=0, microsecond=0)
            if proximo > agora:
                return proximo

    return None


def truncar_texto(texto, max_length=50):
    """Trunca texto longo adicionando reticências"""
    if not texto:
        return ""

    if len(texto) <= max_length:
        return texto

    return texto[:max_length - 3] + "..."


def sanitizar_nome_arquivo(nome):
    """Remove caracteres inválidos de nome de arquivo"""
    # Remove caracteres especiais, mantém apenas alfanuméricos, hífen e underscore
    nome_limpo = re.sub(r'[^\w\s-]', '', nome)
    nome_limpo = re.sub(r'[-\s]+', '-', nome_limpo)
    return nome_limpo.strip('-_')


def eh_horario_valido(horario_str):
    """Valida se string é horário válido (HH:MM)"""
    try:
        hora, minuto = map(int, horario_str.split(':'))
        return 0 <= hora < 24 and 0 <= minuto < 60
    except:
        return False
