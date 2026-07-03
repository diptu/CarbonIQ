import { Sidebar } from "@/components/app/Sidebar";
import { Topbar } from "@/components/app/Topbar";

export default function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <>
      <Sidebar />
      <div className="lg:ml-64 min-h-screen flex flex-col">
        <Topbar />
        <main className="flex-1 relative z-10">{children}</main>
        <footer className="px-6 lg:px-12 py-8 border-t border-white/5 text-on-surface-variant/40 text-[12px] flex flex-col md:flex-row justify-between items-center gap-4">
          <span>
            © {new Date().getFullYear()} CarbonIQ Decentralized Autonomous
            Protocol
          </span>
          <div className="flex items-center gap-2">
            <div className="w-1.5 h-1.5 rounded-full bg-primary-container" />
            <span>All systems operational</span>
          </div>
        </footer>
      </div>
    </>
  );
}
