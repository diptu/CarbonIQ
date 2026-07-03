import Link from "next/link";

export function Topbar() {
  return (
    <header className="sticky top-0 w-full z-40 h-20 bg-surface/60 backdrop-blur-xl border-b border-white/10 flex items-center justify-between px-6 lg:px-12">
      <div className="flex items-center gap-8">
        <div className="hidden md:flex items-center bg-surface-container px-4 py-2 rounded-full border border-white/5 w-80">
          <span className="material-symbols-outlined text-on-surface-variant text-[20px]">
            search
          </span>
          <input
            className="bg-transparent border-none focus:ring-0 text-sm text-on-surface placeholder:text-on-surface-variant/50 w-full outline-none"
            placeholder="Search projects or hash..."
            type="text"
          />
        </div>
      </div>
      <div className="flex items-center gap-6">
        <div className="hidden md:flex items-center gap-3">
          <Link
            href="/notifications"
            className="material-symbols-outlined text-on-surface-variant hover:text-primary transition-colors"
          >
            notifications
          </Link>
          <span className="material-symbols-outlined text-on-surface-variant hover:text-primary cursor-pointer transition-colors">
            settings
          </span>
        </div>
        <button className="bg-surface-variant/40 border border-primary-container/30 px-5 py-2 rounded-full flex items-center gap-3 hover:bg-surface-variant transition-all">
          <div className="w-2 h-2 rounded-full bg-primary-container animate-pulse shadow-[0_0_8px_rgba(0,255,157,0.8)]" />
          <span className="font-label-md text-label-md tracking-wider text-primary">
            0x...F3A2
          </span>
        </button>
      </div>
    </header>
  );
}
