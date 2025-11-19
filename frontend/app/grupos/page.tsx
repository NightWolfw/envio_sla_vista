import { getGrupoFiltros, getGrupos } from "../../lib/api";
import GroupsPageClient from "../../components/GroupsPageClient";

export default async function GruposPage() {
  const [grupos, filtros] = await Promise.all([getGrupos(), getGrupoFiltros()]);
  return <GroupsPageClient grupos={grupos} filtros={filtros} />;
}
