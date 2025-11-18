import { getStats, type OverviewStats } from "../lib/api";
import HomeContent from "../components/HomeContent";

export default async function HomePage() {
  const fallbackStats: OverviewStats = {
    total_grupos: 0,
    total_mensagens: 0,
    total_envios: 0,
    generated_at: new Date().toISOString()
  };

  let stats = fallbackStats;
  try {
    stats = await getStats();
  } catch (error) {
    console.error("Falha ao carregar estatísticas iniciais", error);
  }

  return <HomeContent stats={stats} />;
}
