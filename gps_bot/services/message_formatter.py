# services/message_formatter.py

from datetime import datetime


class MessageFormatter:
    @staticmethod
    def formatar_resumo(cr, total_realizadas, total_pendentes, total_nao_realizadas):
        """
        Formata mensagem resumida para ser enviada ao grupo WhatsApp.

        :param cr: Código do contrato
        :param total_realizadas: Número total de tarefas realizadas
        :param total_pendentes: Número total de tarefas pendentes
        :param total_nao_realizadas: Número total de tarefas não realizadas
        :return: String formatada para envio
        """
        mensagem = (
            f"📋 *RELATÓRIO RESUMIDO*\n"
            f"🏢 Contrato: {cr}\n"
            f"⏰ Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
            f"Tarefas realizadas: {total_realizadas}\n"
            f"Tarefas pendentes: {total_pendentes}\n"
            f"Tarefas não realizadas: {total_nao_realizadas}\n\n"
            f"Detalhes completos das tarefas pendentes e não realizadas foram enviados em anexo no PDF."
        )
        return mensagem
