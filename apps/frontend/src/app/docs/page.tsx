import type { Metadata } from "next";
import Link from "next/link";
import { GlassCard, Logo } from "@/components/ui";
import { CodeTabs } from "./CodeTabs";

export const metadata: Metadata = {
  title: "Developer Documentation Hub",
  description: "Access the foundational layer of CarbonIQ's climate data ecosystem.",
};

const SIDEBAR_MAIN = [
  { icon: "menu_book", label: "Introduction" },
  { icon: "rocket_launch", label: "Quickstart" },
  { icon: "api", label: "API Reference", active: true },
  { icon: "account_balance_wallet", label: "Web3 Integration" },
  { icon: "verified", label: "CIP Standards" },
];

const SIDEBAR_SDKS = [
  { icon: "javascript", label: "Javascript / TS" },
  { icon: "terminal", label: "Python" },
];

const FEATURES = [
  {
    icon: "monitoring",
    title: "Real-time Telemetry",
    description:
      "Access raw IoT data from reforestation projects worldwide with sub-second latency.",
  },
  {
    icon: "security",
    title: "Immutable Proofs",
    description:
      "Every data point is cryptographically signed and anchored to Ethereum via Zero-Knowledge proofs.",
  },
];

const ON_THIS_PAGE = [
  "Authentication",
  "REST endpoints",
  "GraphQL Schema",
  "Webhooks",
  "Error Codes",
];

export default function DocsPage() {
  return (
    <div className="bg-background text-on-surface min-h-screen">
      <nav className="fixed top-0 w-full z-50 flex justify-between items-center px-margin-mobile md:px-margin-desktop h-16 bg-surface/60 backdrop-blur-lg border-b border-white/10">
        <div className="flex items-center gap-8">
          <Link
            href="/"
            className="flex items-center gap-2 font-headline-md text-headline-md font-bold text-primary"
          >
            <Logo size={22} />
            CarbonIQ
          </Link>
          <div className="hidden md:flex gap-6">
            <Link
              href="/governance"
              className="text-on-surface-variant hover:text-on-surface font-label-md text-label-md transition-colors"
            >
              Governance
            </Link>
            <Link
              href="/pricing"
              className="text-on-surface-variant hover:text-on-surface font-label-md text-label-md transition-colors"
            >
              Pricing
            </Link>
            <span className="text-primary border-b-2 border-primary pb-1 font-label-md text-label-md">
              Docs
            </span>
          </div>
        </div>
        <Link
          href="/login"
          className="bg-primary-container text-on-primary-container px-4 py-2 rounded-lg font-label-md text-label-md hover:bg-primary-fixed transition-colors active:scale-95"
        >
          Connect Wallet
        </Link>
      </nav>

      <div className="flex pt-16 min-h-screen">
        <aside className="hidden lg:flex flex-col fixed left-0 top-16 bottom-0 z-40 bg-surface-container-low/80 backdrop-blur-xl border-r border-white/10 w-64 p-6">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-8 h-8 rounded-lg bg-primary-container flex items-center justify-center">
              <span className="material-symbols-outlined text-on-primary-container">
                dataset
              </span>
            </div>
            <div>
              <h2 className="font-headline-sm text-headline-sm font-bold text-primary leading-tight">
                Developer Hub
              </h2>
              <p className="text-body-sm font-body-sm text-on-surface-variant opacity-60">
                v2.1.0-beta
              </p>
            </div>
          </div>
          <nav className="flex-1 space-y-1 overflow-y-auto">
            <div className="text-[10px] font-bold text-on-surface-variant/40 tracking-widest uppercase mb-2 px-3">
              Main Concepts
            </div>
            {SIDEBAR_MAIN.map((item) => (
              <div
                key={item.label}
                className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-all duration-200 ${
                  item.active
                    ? "text-primary bg-primary/10 border-r-2 border-primary"
                    : "text-on-surface-variant hover:bg-white/5 hover:text-on-surface"
                }`}
              >
                <span className="material-symbols-outlined text-[20px]">
                  {item.icon}
                </span>
                <span className="font-label-md text-label-md">
                  {item.label}
                </span>
              </div>
            ))}
            <div className="mt-8 text-[10px] font-bold text-on-surface-variant/40 tracking-widest uppercase mb-2 px-3">
              SDKs
            </div>
            {SIDEBAR_SDKS.map((item) => (
              <div
                key={item.label}
                className="flex items-center gap-3 px-3 py-2 rounded-lg text-on-surface-variant hover:bg-white/5 transition-all"
              >
                <span className="material-symbols-outlined text-[20px]">
                  {item.icon}
                </span>
                <span className="font-label-md text-label-md">
                  {item.label}
                </span>
              </div>
            ))}
          </nav>
        </aside>

        <main className="flex-1 lg:ml-64 px-margin-mobile md:px-margin-desktop py-12 max-w-5xl">
          <nav className="flex items-center gap-2 text-on-surface-variant/60 font-label-sm text-label-sm mb-6">
            <Link href="/" className="hover:text-primary transition-colors">
              Home
            </Link>
            <span className="material-symbols-outlined text-xs">
              chevron_right
            </span>
            <span className="text-on-surface">API Reference</span>
          </nav>

          <header className="mb-12">
            <h1 className="font-headline-xl text-headline-xl text-primary mb-4">
              API Reference
            </h1>
            <p className="text-body-lg font-body-lg text-on-surface-variant max-w-2xl leading-relaxed">
              Access the foundational layer of CarbonIQ&apos;s climate data
              ecosystem. Our REST and GraphQL APIs enable you to
              programmatically verify carbon offsets, query ledger states,
              and integrate climate-positive actions into any dApp.
            </p>
            <div className="flex gap-4 mt-8">
              <div className="px-4 py-2 rounded-full border border-primary-container/30 bg-primary-container/5 text-primary-container font-label-md text-label-md flex items-center gap-2 verified-badge-glow">
                <span className="material-symbols-outlined text-sm">
                  check_circle
                </span>
                Verified Stable v2.1.0
              </div>
              <div className="px-4 py-2 rounded-full border border-white/10 bg-white/5 text-on-surface-variant font-label-md text-label-md flex items-center gap-2">
                <span className="material-symbols-outlined text-sm">
                  timer
                </span>
                Average Latency: 42ms
              </div>
            </div>
          </header>

          <section className="mb-16">
            <h2 className="font-headline-lg text-headline-lg text-primary mb-6 border-b border-white/5 pb-2">
              Authentication
            </h2>
            <p className="text-body-md font-body-md text-on-surface-variant mb-6">
              All API requests must be authenticated using a Bearer token in
              the{" "}
              <code className="bg-white/10 px-1.5 py-0.5 rounded font-mono text-sm text-primary">
                Authorization
              </code>{" "}
              header. You can generate tokens in your Developer Dashboard.
            </p>
            <CodeTabs />
          </section>

          <section className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-16">
            {FEATURES.map((feature) => (
              <GlassCard key={feature.title} className="p-8 group">
                <div className="w-12 h-12 rounded-lg bg-secondary-container/20 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                  <span className="material-symbols-outlined text-secondary">
                    {feature.icon}
                  </span>
                </div>
                <h3 className="font-headline-md text-headline-md text-primary mb-3">
                  {feature.title}
                </h3>
                <p className="text-body-md font-body-md text-on-surface-variant leading-relaxed">
                  {feature.description}
                </p>
              </GlassCard>
            ))}
          </section>

          <footer className="w-full py-12 flex flex-col md:flex-row justify-between items-center gap-6 border-t border-white/10">
            <div className="flex flex-col gap-2">
              <span className="text-label-md font-bold text-primary">
                CarbonIQ DAO
              </span>
              <p className="font-body-sm text-body-sm text-on-surface-variant">
                © {new Date().getFullYear()} CarbonIQ DAO. Verified on
                Ethereum.
              </p>
            </div>
          </footer>
        </main>

        <aside className="hidden xl:block w-64 p-12 pr-margin-desktop">
          <h4 className="font-label-sm text-label-sm font-bold text-on-surface-variant/40 tracking-widest uppercase mb-4">
            On This Page
          </h4>
          <ul className="space-y-4 font-label-md text-label-md">
            {ON_THIS_PAGE.map((item, i) => (
              <li key={item}>
                <span
                  className={
                    i === 0
                      ? "text-primary"
                      : "text-on-surface-variant hover:text-primary transition-colors"
                  }
                >
                  {item}
                </span>
              </li>
            ))}
          </ul>
          <div className="mt-12 p-6 glass-card rounded-xl bg-primary-container/5">
            <span className="material-symbols-outlined text-primary-container mb-2 block">
              lightbulb
            </span>
            <p className="text-body-sm font-body-sm text-on-surface leading-tight">
              Need a custom integration? Our team is available for
              architectural reviews.
            </p>
          </div>
        </aside>
      </div>
    </div>
  );
}
