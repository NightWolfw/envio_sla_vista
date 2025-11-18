"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navItems = [
  { href: "/", label: "Visão Geral" },
  { href: "/dashboard", label: "Dashboard" },
  { href: "/grupos", label: "Grupos" },
  { href: "/agendamentos", label: "Agendamentos" },
  { href: "/mensagens", label: "Mensagens" },
  { href: "/sla", label: "SLA / Preview" },
  { href: "/envio", label: "Envio Manual" }
];

export default function Sidebar() {
  const pathname = usePathname();
  return (
    <aside className="sidebar">
      <div>
        <h1 style={{ margin: 0, fontSize: "1.3rem" }}>GPS Vista</h1>
        <p style={{ margin: "0.25rem 0 0", color: "var(--text-muted)", fontSize: "0.9rem" }}>
          Painel administrativo
        </p>
      </div>
      <nav style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
        {navItems.map((item) => {
          const active = pathname === item.href;
          return (
            <Link key={item.href} href={item.href} className={active ? "active" : ""}>
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
