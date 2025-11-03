from database.connection import buscar_grupos_whatsapp, buscar_grupos_por_cr
import pandas as pd


class GruposReader:
    def __init__(self):
        """Inicializa o leitor de grupos usando banco de dados ao invés de Excel"""
        pass

    def obter_grupos_filtrados(self, horario: str):
        """
        Busca grupos do banco de dados que devem receber mensagens no horário passado.
        
        :param horario: horário no formato 'HH:MM'
        :return: lista de dicionários com as colunas ID, Nome do Grupo e CR
        """
        # Busca todos os grupos ativos do banco
        df = buscar_grupos_whatsapp()
        
        if df.empty:
            print("⚠️  Nenhum grupo encontrado no banco de dados")
            return []
        
        # Ajusta o CR para string, substituindo NaN por string vazia
        df['CR'] = df['CR'].fillna('').astype(str)
        
        # Filtra apenas grupos com Envio = True
        df = df[df['Envio'] == True]
        
        if df.empty:
            print(f"ℹ️  Nenhum grupo configurado para envio no horário {horario}")
            return []
        
        horarios_fixos = ['06:00', '12:00', '18:00']
        
        def filtro_horario(row):
            if row['DiaTodo'] == True:
                return True
            elif row['DiaTodo'] == False and horario in horarios_fixos:
                return True
            else:
                return False
        
        df = df[df.apply(filtro_horario, axis=1)]
        
        if df.empty:
            print(f"ℹ️  Nenhum grupo deve receber mensagens no horário {horario}")
            return []
        
        # Normalizar nomes de colunas para evitar espaços no dicionário retornado
        df.rename(columns=lambda x: x.strip(), inplace=True)
        
        grupos_filtrados = df[['ID', 'Nome do Grupo', 'CR']].to_dict(orient='records')
        
        print(f"✓ {len(grupos_filtrados)} grupos selecionados para envio às {horario}")
        for grupo in grupos_filtrados:
            print(f"  - {grupo['Nome do Grupo']} (CR: {grupo['CR']})")
            
        return grupos_filtrados
    
    def obter_grupos_por_cr(self, cr_list):
        """
        Busca grupos específicos por lista de CRs
        
        :param cr_list: lista de CRs
        :return: DataFrame com os grupos encontrados
        """
        return buscar_grupos_por_cr(cr_list)
    
    def verificar_grupos_ativos(self):
        """
        Verifica quantos grupos estão ativos no banco
        
        :return: número total de grupos ativos
        """
        df = buscar_grupos_whatsapp()
        total = len(df)
        envio_ativo = len(df[df['Envio'] == True]) if not df.empty else 0
        
        print(f"📊 Resumo dos grupos:")
        print(f"  - Total de grupos: {total}")
        print(f"  - Com envio ativo: {envio_ativo}")
        
        return total