import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd
from datetime import datetime, timedelta


def conectar_bd():
    """Conecta ao banco de dados PostgreSQL usando as credenciais fornecidas"""
    return psycopg2.connect(
        dbname="dw_sla",
        user="jonatan_lopes",
        password="Jl2@24Jl",
        host="localhost",
        port="5433"
    )


def buscar_grupos_whatsapp():
    """
    Busca os dados dos grupos WhatsApp diretamente do banco de dados
    Retorna um DataFrame com as mesmas colunas da planilha original
    """
    conn = conectar_bd()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # Query para buscar grupos do WhatsApp com dados de envio
        query = """
        SELECT 
            id as "ID",
            nome_grupo as "Nome do Grupo", 
            envio as "Envio",
            dia_todo as "DiaTodo",
            cr as "CR"
        FROM grupos_whatsapp 
        WHERE ativo = true
        ORDER BY nome_grupo
        """

        cursor.execute(query)
        resultados = cursor.fetchall()

        # Converte para DataFrame pandas mantendo a mesma estrutura da planilha
        df = pd.DataFrame(resultados)

        # Garante que as colunas boolean sejam tratadas corretamente
        if not df.empty:
            df['Envio'] = df['Envio'].fillna(False).astype(bool)
            df['DiaTodo'] = df['DiaTodo'].fillna(False).astype(bool)
            df['CR'] = pd.to_numeric(df['CR'], errors='coerce')

        print(f"✓ Carregados {len(df)} grupos do banco de dados")
        return df

    except Exception as e:
        print(f"✗ Erro ao buscar grupos: {e}")
        return pd.DataFrame()

    finally:
        cursor.close()
        conn.close()


def buscar_grupos_por_cr(cr_list):
    """
    Busca grupos específicos por lista de CRs
    """
    if not cr_list:
        return pd.DataFrame()

    conn = conectar_bd()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # Converte CRs para string para usar com ANY
        cr_strings = [str(cr) for cr in cr_list]

        query = """
        SELECT 
            id as "ID",
            nome_grupo as "Nome do Grupo",
            envio as "Envio", 
            dia_todo as "DiaTodo",
            cr as "CR"
        FROM grupos_whatsapp 
        WHERE ativo = true 
        AND cr = ANY(%s)
        ORDER BY nome_grupo
        """

        cursor.execute(query, (cr_strings,))
        resultados = cursor.fetchall()

        df = pd.DataFrame(resultados)

        if not df.empty:
            df['Envio'] = df['Envio'].fillna(False).astype(bool)
            df['DiaTodo'] = df['DiaTodo'].fillna(False).astype(bool)
            df['CR'] = pd.to_numeric(df['CR'], errors='coerce')

        return df

    except Exception as e:
        print(f"✗ Erro ao buscar grupos por CR: {e}")
        return pd.DataFrame()

    finally:
        cursor.close()
        conn.close()


def testar_conexao():
    """Testa a conexão com o banco de dados"""
    try:
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute('SELECT version();')
        versao = cursor.fetchone()
        cursor.close()
        conn.close()
        print(f"✓ Conexão ao banco OK: {versao[0]}")
        return True
    except Exception as e:
        print(f"✗ Falha na conexão: {e}")
        return False


def verificar_estrutura_tabela():
    """Verifica se a tabela grupos_whatsapp existe e tem a estrutura correta"""
    conn = conectar_bd()
    cursor = conn.cursor()

    try:
        # Verifica se a tabela existe
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'grupos_whatsapp'
            );
        """)

        tabela_existe = cursor.fetchone()[0]

        if not tabela_existe:
            print("⚠️  Tabela 'grupos_whatsapp' não encontrada!")
            print("📋 Script para criar a tabela:")
            print("""
CREATE TABLE grupos_whatsapp (
    id VARCHAR(255) PRIMARY KEY,
    nome_grupo VARCHAR(255) NOT NULL,
    envio BOOLEAN DEFAULT FALSE,
    dia_todo BOOLEAN DEFAULT FALSE, 
    cr NUMERIC,
    ativo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para melhor performance
CREATE INDEX idx_grupos_cr ON grupos_whatsapp(cr);
CREATE INDEX idx_grupos_ativo ON grupos_whatsapp(ativo);
""")
            return False

        # Verifica estrutura das colunas
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'grupos_whatsapp'
            ORDER BY ordinal_position;
        """)

        colunas = cursor.fetchall()
        print("✓ Tabela encontrada com colunas:")
        for coluna in colunas:
            print(f"  - {coluna[0]}: {coluna[1]}")

        return True

    except Exception as e:
        print(f"✗ Erro ao verificar estrutura: {e}")
        return False

    finally:
        cursor.close()
        conn.close()
