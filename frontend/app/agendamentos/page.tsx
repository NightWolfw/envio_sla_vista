import { getAgendamentos, getGrupos } from "../../lib/api";
import AgendamentosClient from "./table";

export default async function AgendamentosPage() {
  const [agendamentos, grupos] = await Promise.all([getAgendamentos(), getGrupos()]);

  return (
    <div className="grid" style={{ gap: "1.5rem" }}>
      <section className="panel">
        <h2>Agendamentos configurados</h2>
        <AgendamentosClient agendamentos={agendamentos} grupos={grupos} />
      </section>
    </div>
  );
}
