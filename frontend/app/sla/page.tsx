import { getGrupos } from "../../lib/api";
import SlaPreviewClient from "./preview";

export default async function SlaPage() {
  const grupos = await getGrupos();
  return (
    <div className="grid" style={{ gap: "1.5rem" }}>
      <section className="panel">
        <h2>Preview de SLA / Envio rápido</h2>
        <SlaPreviewClient grupos={grupos} />
      </section>
    </div>
  );
}
