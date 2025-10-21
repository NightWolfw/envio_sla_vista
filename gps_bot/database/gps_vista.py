from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor
from config import DB_CONFIG


class GPSVistaDB:
    def __init__(self):
        self.config = DB_CONFIG

    def conectar(self):
        return psycopg2.connect(
            host=self.config['host'],
            port=self.config['port'],
            database=self.config['database'],
            user=self.config['user'],
            password=self.config['password']
        )

    def calcular_periodo_consulta(self, horario_envio_str):
        hoje = datetime.now().date()
        horario_envio = datetime.strptime(horario_envio_str, "%H:%M").time()
        datetime_envio = datetime.combine(hoje, horario_envio)

        fim_periodo = datetime_envio - timedelta(minutes=5)
        inicio_periodo = datetime.combine(hoje, datetime.min.time())

        return inicio_periodo.strftime('%Y-%m-%d %H:%M:%S'), fim_periodo.strftime('%Y-%m-%d %H:%M:%S')

    def buscar_tarefas(self, cr_list, horario_envio):
        inicio_periodo, fim_periodo = self.calcular_periodo_consulta(horario_envio)

        conn = self.conectar()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # 🔧 CORREÇÃO: Converter CRs para string antes de passar para ANY
        cr_strings = [str(cr) for cr in cr_list]

        query = """
        SELECT
            A.numero AS "Numero",
            A.status AS "Id_Status",
            A.prazo::date AS "Prazo",
            A.disponibilizacao AS "Disponibilizacao",
            A.inicioreal AS "InicioReal",
            A.terminoreal AS "TerminoReal",
            A.expirada AS "Expirada",
            R.nome AS "Executor",
            A.id AS "Id_Tarefa",
            A.nome AS "Nome_Tarefa"
        FROM dbo.tarefa A
        LEFT JOIN dbo.recurso R ON R.codigohash = A.finalizadoporhash
        INNER JOIN dw_vista.DM_ESTRUTURA E ON E.Id_Estrutura = A.estruturaid
            AND E.crno = ANY(%s)
        WHERE A.disponibilizacao >= %s
          AND A.disponibilizacao < %s
        ORDER BY A.terminoreal NULLS LAST, A.prazo;
        """

        cursor.execute(query, (cr_strings, inicio_periodo, fim_periodo))
        resultados = cursor.fetchall()
        conn.close()

        return resultados

    def testar_conexao(self):
        try:
            conn = self.conectar()
            cursor = conn.cursor()
            cursor.execute('SELECT version();')
            versao = cursor.fetchone()
            conn.close()
            print(f"✓ Conexão ao banco OK: {versao[0]}")
            return True
        except Exception as e:
            print(f"✗ Falha na conexão: {e}")
            return False
