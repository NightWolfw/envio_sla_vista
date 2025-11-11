import pandas as pd
from io import BytesIO
from app.models.database import get_db_site


def importar_excel(caminho_arquivo):
    """Importa grupos do Excel para o banco"""
    df = pd.read_excel(caminho_arquivo)
    conn = get_db_site()
    cur = conn.cursor()

    for _, row in df.iterrows():
        dia_todo = None if pd.isna(row['DiaTodo']) else row['DiaTodo']

        # Formata CR com zeros
        if pd.isna(row['CR']):
            cr = None
        else:
            cr_valor = int(row['CR'])
            cr = f"{cr_valor:05d}"

        # UPSERT
        cur.execute("""
            INSERT INTO grupos_whatsapp (group_id, nome_grupo, envio, dia_todo, cr) 
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (group_id) DO UPDATE 
            SET nome_grupo = EXCLUDED.nome_grupo,
                envio = EXCLUDED.envio,
                dia_todo = EXCLUDED.dia_todo,
                cr = EXCLUDED.cr
        """, (row['ID'], row['Nome do Grupo'], row['Envio'], dia_todo, cr))

    conn.commit()
    cur.close()
    conn.close()


def exportar_excel():
    """Exporta grupos para Excel"""
    conn = get_db_site()
    df = pd.read_sql_query("""
        SELECT group_id as "ID", 
               nome_grupo as "Nome do Grupo", 
               envio as "Envio", 
               dia_todo as "DiaTodo", 
               cr as "CR" 
        FROM grupos_whatsapp 
        ORDER BY id
    """, conn)
    conn.close()

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')

    output.seek(0)
    return output
