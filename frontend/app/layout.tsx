import type { Metadata } from "next";
import "./globals.css";
import Sidebar from "../components/Sidebar";

export const metadata: Metadata = {
  title: "GPS Vista",
  description: "Frontend administrativo conectado ao FastAPI"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR">
      <body className="bg-background text-text font-sans antialiased">
        <div className="layout flex min-h-screen">
          <Sidebar />
          <main className="content flex-1 px-6 py-8">{children}</main>
        </div>
      </body>
    </html>
  );
}
