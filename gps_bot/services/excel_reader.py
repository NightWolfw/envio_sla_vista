import pandas as pd
from config import EXCEL_PATH


class GruposReader:
    def __init__(self, caminho=EXCEL_PATH):
        self.caminho = caminho

    def obter_grupos_filtrados(self, horario: str):
        """
        Lê a planilha Excel e retorna grupos que devem receber mensagens no horário passado.

        :param horario: horário no formato 'HH:MM'
        :return: lista de dicionários com as colunas ID, Nome do Grupo e CR
        """
        df = pd.read_excel(self.caminho)

        # Ajusta o CR para string, substituindo NaN por string vazia
        df['CR'] = df['CR'].fillna('').astype(str)

        # Filtra apenas grupos com Envio = True
        df = df[df['Envio'] == True]

        horarios_fixos = ['06:00', '12:00', '18:00']

        def filtro_horario(row):
            if row['DiaTodo'] == True:
                return True
            elif row['DiaTodo'] == False and horario in horarios_fixos:
                return True
            else:
                return False

        df = df[df.apply(filtro_horario, axis=1)]

        # Normalizar nomes de colunas para evitar espaços no dicionário retornado
        df.rename(columns=lambda x: x.strip(), inplace=True)

        grupos_filtrados = df[['ID', 'Nome do Grupo', 'CR']].to_dict(orient='records')
        return grupos_filtrados
