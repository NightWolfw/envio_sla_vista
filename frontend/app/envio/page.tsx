import { getEnvioGrupos } from "../../lib/api";
import EnvioForm from "./form";

export default async function EnvioPage() {
  const grupos = await getEnvioGrupos();
  return (
    <div className="grid" style={{ gap: "1.5rem" }}>
      <section className="panel">
        <h2>Envio manual de mensagens</h2>
        <EnvioForm grupos={grupos} />
      </section>
    </div>
  );
}
