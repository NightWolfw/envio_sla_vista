import { getGrupos, getMensagens } from "../../lib/api";
import MensagensClient from "./table";

export default async function MensagensPage() {
  const [mensagens, grupos] = await Promise.all([getMensagens(), getGrupos()]);

  return (
    <div className="grid" style={{ gap: "1.5rem" }}>
      <section className="panel">
        <h2>Mensagens agendadas</h2>
        <MensagensClient mensagens={mensagens} grupos={grupos} />
      </section>
    </div>
  );
}
