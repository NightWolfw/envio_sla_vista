"""
Serviço para atualização de dados da estrutura organizacional (Vista)
"""
from app.models.database import get_db_site, get_db_vista


def atualizar_dados_estrutura():
    """
    Atualiza dados de estrutura organizacional dos grupos
    Busca informações do banco Vista (dw_gps) e atualiza no banco SLA (dw_sla)
    """
    print("🔄 Iniciando atualização de estrutura...")

    conn_sla = get_db_site()
    conn_vista = get_db_vista()

    cur_sla = conn_sla.cursor()
    cur_vista = conn_vista.cursor()

    try:
        # Busca grupos com CR definido
        cur_sla.execute("""
            SELECT id, cr 
            FROM grupos_whatsapp 
            WHERE cr IS NOT NULL AND cr != ''
        """)

        grupos = cur_sla.fetchall()
        total = len(grupos)
        atualizados = 0
        erros = 0

        print(f"📊 Total de grupos para atualizar: {total}")

        for grupo_id, cr in grupos:
            try:
                cr_com_zeros = cr
                cr_sem_zeros = cr.lstrip('0') if cr else '0'

                # Busca dados da estrutura no Vista
                cur_vista.execute("""
                    SELECT 
                        cliente,
                        nivel_01 as pec_01,
                        nivel_02 as pec_02,
                        id_cr
                    FROM dw_vista.dm_estrutura
                    WHERE crno::text = %s OR crno::text = %s
                    LIMIT 1
                """, (cr_com_zeros, cr_sem_zeros))

                estrutura = cur_vista.fetchone()

                if estrutura:
                    cliente, pec_01, pec_02, id_cr = estrutura

                    # Busca gestores
                    cur_vista.execute("""
                        SELECT 
                            diretorexecutivo,
                            diretorregional,
                            gerenteregional,
                            gerente,
                            supervisor
                        FROM dw_vista.dm_cr
                        WHERE id_cr = %s
                        LIMIT 1
                    """, (id_cr,))

                    gestores = cur_vista.fetchone()

                    if gestores:
                        diretor_exec, diretor_reg, gerente_reg, gerente, supervisor = gestores

                        # Atualiza no banco SLA
                        cur_sla.execute("""
                            UPDATE grupos_whatsapp
                            SET cliente = %s,
                                pec_01 = %s,
                                pec_02 = %s,
                                diretorexecutivo = %s,
                                diretorregional = %s,
                                gerenteregional = %s,
                                gerente = %s,
                                supervisor = %s,
                                ultima_atualizacao = CURRENT_TIMESTAMP
                            WHERE id = %s
                        """, (cliente, pec_01, pec_02, diretor_exec, diretor_reg,
                              gerente_reg, gerente, supervisor, grupo_id))

                        atualizados += 1
                        print(f"  ✅ Grupo {grupo_id} (CR {cr}) atualizado")

            except Exception as e:
                erros += 1
                print(f"  ❌ Erro ao processar grupo {grupo_id}: {str(e)}")

        conn_sla.commit()

        print(f"\n{'=' * 60}")
        print(f"✅ Atualização concluída!")
        print(f"   Total: {total} | Atualizados: {atualizados} | Erros: {erros}")
        print(f"{'=' * 60}\n")

        return {
            'total': total,
            'atualizados': atualizados,
            'erros': erros
        }

    except Exception as e:
        conn_sla.rollback()
        print(f"❌ Erro na atualização: {str(e)}")
        raise
    finally:
        cur_sla.close()
        cur_vista.close()
        conn_sla.close()
        conn_vista.close()


def atualizar_grupo_especifico(grupo_id):
    """Atualiza estrutura de um grupo específico"""
    conn_sla = get_db_site()
    conn_vista = get_db_vista()

    cur_sla = conn_sla.cursor()
    cur_vista = conn_vista.cursor()

    try:
        # Busca CR do grupo
        cur_sla.execute("SELECT cr FROM grupos_whatsapp WHERE id = %s", (grupo_id,))
        resultado = cur_sla.fetchone()

        if not resultado or not resultado[0]:
            return False

        cr = resultado[0]
        cr_com_zeros = cr
        cr_sem_zeros = cr.lstrip('0') if cr else '0'

        # Busca estrutura no Vista
        cur_vista.execute("""
            SELECT cliente, nivel_01, nivel_02, id_cr
            FROM dw_vista.dm_estrutura
            WHERE crno::text = %s OR crno::text = %s
            LIMIT 1
        """, (cr_com_zeros, cr_sem_zeros))

        estrutura = cur_vista.fetchone()

        if not estrutura:
            return False

        cliente, pec_01, pec_02, id_cr = estrutura

        # Busca gestores
        cur_vista.execute("""
            SELECT diretorexecutivo, diretorregional, gerenteregional, gerente, supervisor
            FROM dw_vista.dm_cr
            WHERE id_cr = %s
            LIMIT 1
        """, (id_cr,))

        gestores = cur_vista.fetchone()

        if not gestores:
            return False

        diretor_exec, diretor_reg, gerente_reg, gerente, supervisor = gestores

        # Atualiza grupo
        cur_sla.execute("""
            UPDATE grupos_whatsapp
            SET cliente = %s, pec_01 = %s, pec_02 = %s,
                diretorexecutivo = %s, diretorregional = %s,
                gerenteregional = %s, gerente = %s, supervisor = %s,
                ultima_atualizacao = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (cliente, pec_01, pec_02, diretor_exec, diretor_reg, gerente_reg, gerente, supervisor, grupo_id))

        conn_sla.commit()
        return True

    except Exception as e:
        conn_sla.rollback()
        print(f"Erro ao atualizar grupo {grupo_id}: {e}")
        return False
    finally:
        cur_sla.close()
        cur_vista.close()
        conn_sla.close()
        conn_vista.close()
