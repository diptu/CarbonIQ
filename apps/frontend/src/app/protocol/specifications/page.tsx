import type { Metadata } from "next";
import Link from "next/link";
import { GlassCard, Logo } from "@/components/ui";

export const metadata: Metadata = {
  title: "Protocol Specifications",
  description: "Technical control plane for the CarbonIQ Protocol.",
};

const STAT_CARDS = [
  {
    icon: "groups",
    label: "Total Active Nodes",
    value: "124",
    trend: "+3.2% from Epoch 142",
    trendIcon: "trending_up",
  },
  {
    icon: "verified_user",
    label: "Active Validators",
    value: "89",
    trend: "Quorum Threshold Reached",
    trendIcon: "check_circle",
  },
  {
    icon: "signal_cellular_alt",
    label: "Network Health",
    value: "99.9%",
    trend: "Latency: 14ms",
    trendIcon: "bolt",
  },
  {
    icon: "eco",
    label: "Carbon Offset Index",
    value: "14.2M",
    trend: "Verified MTCO2e",
    trendIcon: "bolt",
  },
];

const ARCHITECTURE_LAYERS = [
  {
    level: "L4",
    title: "Ledger Anchor",
    description:
      "Immutable settlement layer for verified carbon credits and ownership titles.",
    icon: "anchor",
  },
  {
    level: "L3",
    title: "BFT Consensus",
    description:
      "Proof of Integrity algorithm ensuring deterministic finality across 120+ nodes.",
    icon: "sync_alt",
  },
  {
    level: "L2",
    title: "AI Neural Inference",
    description:
      "Satellite and LIDAR processing for real-time sequestration modeling.",
    icon: "psychology",
  },
  {
    level: "L1",
    title: "IoT Ingestion",
    description:
      "Zero-knowledge sensor connectivity for ground-level emission tracking.",
    icon: "sensors",
  },
];

const NODES = [
  { id: "N-7741-EU", region: "Frankfurt, DE", uptime: "99.98%" },
  { id: "N-1202-NA", region: "Oregon, US", uptime: "100.0%" },
  { id: "N-9088-AS", region: "Singapore, SG", uptime: "99.91%" },
];

const CIPS = [
  {
    id: "CIP-124: dynamic_oracle_pricing",
    description: "Optimization of land-use API frequency.",
    status: "64% VOTED",
  },
  {
    id: "CIP-125: sharding_implementation",
    description: "Parallelizing credit verification.",
    status: "PROPOSED",
  },
];

const CONTRACTS = [
  { name: "Verification Engine", address: "0x7F22...8C11" },
  { name: "Credit Registry", address: "0x14A9...F442" },
];

const ENDPOINTS = [
  { name: "Mainnet RPC", status: "UP" },
  { name: "Indexing DB", status: "UP" },
  { name: "Graph API", status: "UP" },
  { name: "Archive Node", status: "SYNCING" },
];

const SIDEBAR_LINKS = [
  { icon: "layers", label: "Architecture", active: true },
  { icon: "hub", label: "Node Status" },
  { icon: "account_balance", label: "Governance" },
  { icon: "description", label: "Smart Contracts" },
  { icon: "menu_book", label: "Documentation" },
];

export default function ProtocolSpecificationsPage() {
  return (
    <div className="grid-bg min-h-screen">
      <header className="fixed top-0 w-full z-50 flex justify-between items-center px-margin-mobile md:px-margin-desktop h-20 bg-surface-dim/60 backdrop-blur-xl border-b border-white/10">
        <div className="flex items-center gap-8">
          <Link
            href="/"
            className="flex items-center gap-2 font-headline-md text-headline-md font-bold text-primary tracking-tight"
          >
            <Logo size={24} />
            CarbonIQ Protocol
          </Link>
          <nav className="hidden md:flex gap-6 items-center">
            <span className="text-primary font-bold border-b-2 border-primary pb-1 p-2">
              Architecture
            </span>
            <Link
              href="/governance"
              className="text-on-surface-variant font-medium hover:text-primary transition-colors p-2 rounded"
            >
              Governance
            </Link>
            <Link
              href="/docs"
              className="text-on-surface-variant font-medium hover:text-primary transition-colors p-2 rounded"
            >
              Explorer
            </Link>
          </nav>
        </div>
        <Link
          href="/login"
          className="bg-primary-container text-on-primary-container px-6 py-2 rounded-full font-bold active:scale-95 transition-transform"
        >
          Connect Wallet
        </Link>
      </header>

      <div className="flex pt-20">
        <aside className="hidden lg:flex flex-col h-[calc(100vh-80px)] w-72 sticky top-20 bg-surface-container-low/80 backdrop-blur-2xl border-r border-white/5">
          <div className="p-6 border-b border-white/5">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center border border-primary/20">
                <span className="material-symbols-outlined text-primary">
                  hub
                </span>
              </div>
              <div>
                <p className="font-headline-md text-headline-md text-primary leading-none">
                  Protocol Core
                </p>
                <p className="text-[10px] text-on-surface-variant uppercase tracking-widest mt-1">
                  Mainnet v2.4.0
                </p>
              </div>
            </div>
          </div>
          <nav className="flex-1 p-4 space-y-2">
            {SIDEBAR_LINKS.map((link) => (
              <div
                key={link.label}
                className={`flex items-center gap-4 p-3 rounded-lg transition-all ${
                  link.active
                    ? "bg-primary-container/20 text-primary border-r-4 border-primary"
                    : "text-on-surface-variant hover:text-on-surface hover:bg-white/5"
                }`}
              >
                <span className="material-symbols-outlined">
                  {link.icon}
                </span>
                <span className="font-label-md text-label-md">
                  {link.label}
                </span>
              </div>
            ))}
          </nav>
        </aside>

        <main className="flex-1 relative z-10 px-margin-mobile md:px-margin-desktop py-12">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-gutter mb-12">
            {STAT_CARDS.map((card) => (
              <GlassCard key={card.label} className="p-6 relative overflow-hidden">
                <p className="text-on-surface-variant font-label-md text-label-md uppercase tracking-wider">
                  {card.label}
                </p>
                <h2 className="font-headline-xl text-headline-xl text-primary mt-2">
                  {card.value}
                </h2>
                <p className="text-primary-container text-body-sm flex items-center gap-1 mt-2">
                  <span className="material-symbols-outlined text-sm">
                    {card.trendIcon}
                  </span>
                  {card.trend}
                </p>
              </GlassCard>
            ))}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-gutter mb-12">
            <div className="lg:col-span-7 flex flex-col gap-6">
              <h3 className="font-headline-lg text-headline-lg text-primary">
                Protocol Architecture
              </h3>
              <div className="space-y-4">
                {ARCHITECTURE_LAYERS.map((layer) => (
                  <GlassCard
                    key={layer.level}
                    className="p-4 border-l-4 border-l-primary flex items-center gap-6"
                  >
                    <div className="w-16 text-center">
                      <p className="text-primary font-bold text-xs">
                        {layer.level}
                      </p>
                    </div>
                    <div className="flex-1">
                      <h4 className="font-headline-md text-headline-md text-primary mb-1">
                        {layer.title}
                      </h4>
                      <p className="text-on-surface-variant text-body-sm">
                        {layer.description}
                      </p>
                    </div>
                    <span className="material-symbols-outlined text-primary">
                      {layer.icon}
                    </span>
                  </GlassCard>
                ))}
              </div>
            </div>

            <div className="lg:col-span-5">
              <GlassCard className="h-full flex flex-col overflow-hidden">
                <div className="p-6 border-b border-white/5">
                  <h3 className="font-headline-md text-headline-md text-primary">
                    Global Distribution
                  </h3>
                </div>
                <div className="flex-1 relative min-h-[300px]">
                  <div className="absolute inset-0 opacity-20 flex items-center justify-center p-8">
                    <span className="material-symbols-outlined text-[160px] text-primary">
                      public
                    </span>
                  </div>
                  <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-[#062C22] to-transparent">
                    <div className="space-y-2">
                      <div className="flex justify-between text-[10px] uppercase font-bold text-on-surface-variant">
                        <span>Node ID</span>
                        <span>Region</span>
                        <span>Uptime</span>
                      </div>
                      {NODES.map((node) => (
                        <div
                          key={node.id}
                          className="flex justify-between text-xs text-primary font-mono border-b border-white/5 pb-1"
                        >
                          <span>{node.id}</span>
                          <span>{node.region}</span>
                          <span className="text-primary-container">
                            {node.uptime}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </GlassCard>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-gutter">
            <GlassCard className="p-8">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <span className="material-symbols-outlined text-primary text-3xl">
                    account_balance
                  </span>
                  <h3 className="font-headline-lg text-headline-lg text-primary">
                    Governance
                  </h3>
                </div>
                <span className="text-on-surface-variant font-mono text-sm px-3 py-1 border border-white/10 rounded">
                  v2.4.0
                </span>
              </div>
              <div className="grid grid-cols-2 gap-4 mb-8">
                <div className="p-4 bg-white/5 rounded-xl border border-white/10">
                  <p className="text-on-surface-variant text-[10px] uppercase tracking-widest mb-1">
                    Mechanism
                  </p>
                  <p className="text-primary font-bold">Proof of Integrity</p>
                </div>
                <div className="p-4 bg-white/5 rounded-xl border border-white/10">
                  <p className="text-on-surface-variant text-[10px] uppercase tracking-widest mb-1">
                    Voting Period
                  </p>
                  <p className="text-primary font-bold">72 Epochs</p>
                </div>
              </div>
              <h4 className="text-label-md font-label-md text-on-surface-variant uppercase tracking-widest mb-4">
                Active CIPs
              </h4>
              <div className="space-y-3">
                {CIPS.map((cip) => (
                  <div
                    key={cip.id}
                    className="flex items-center gap-4 p-3 hover:bg-white/5 rounded-lg border border-transparent hover:border-white/10 transition-all"
                  >
                    <div className="w-2 h-2 rounded-full bg-secondary" />
                    <div className="flex-1">
                      <p className="text-sm font-bold text-primary">
                        {cip.id}
                      </p>
                      <p className="text-xs text-on-surface-variant">
                        {cip.description}
                      </p>
                    </div>
                    <span className="text-xs font-mono text-secondary">
                      {cip.status}
                    </span>
                  </div>
                ))}
              </div>
            </GlassCard>

            <GlassCard className="p-8">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <span className="material-symbols-outlined text-secondary text-3xl">
                    terminal
                  </span>
                  <h3 className="font-headline-lg text-headline-lg text-primary">
                    Technical Specs
                  </h3>
                </div>
                <div className="flex items-center gap-2 px-2 py-1 bg-green-500/10 border border-green-500/30 rounded">
                  <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                  <span className="text-[10px] font-bold text-green-400">
                    OPERATIONAL
                  </span>
                </div>
              </div>
              <div className="space-y-6">
                <div>
                  <p className="text-label-md font-label-md text-on-surface-variant uppercase tracking-widest mb-3">
                    Core Smart Contracts
                  </p>
                  <div className="space-y-3">
                    {CONTRACTS.map((contract) => (
                      <div
                        key={contract.name}
                        className="flex items-center justify-between bg-black/20 p-3 rounded-lg border border-white/5"
                      >
                        <span className="text-sm text-on-surface-variant font-mono">
                          {contract.name}
                        </span>
                        <code className="text-xs text-primary font-mono bg-white/5 px-2 py-1 rounded">
                          {contract.address}
                        </code>
                      </div>
                    ))}
                  </div>
                </div>
                <div>
                  <p className="text-label-md font-label-md text-on-surface-variant uppercase tracking-widest mb-3">
                    API Endpoint Status
                  </p>
                  <div className="grid grid-cols-2 gap-4">
                    {ENDPOINTS.map((endpoint) => (
                      <div
                        key={endpoint.name}
                        className="flex items-center justify-between p-3 rounded-lg bg-white/5"
                      >
                        <span className="text-xs font-mono">
                          {endpoint.name}
                        </span>
                        <span
                          className={`text-[10px] font-bold ${
                            endpoint.status === "UP"
                              ? "text-primary-container"
                              : "text-secondary"
                          }`}
                        >
                          {endpoint.status}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </GlassCard>
          </div>
        </main>
      </div>

      <footer className="w-full py-12 px-margin-mobile md:px-margin-desktop border-t border-white/10 bg-surface-container-lowest flex flex-col md:flex-row justify-between items-center gap-6 relative z-10">
        <div className="flex flex-col gap-2">
          <span className="font-headline-md text-headline-md text-primary">
            CarbonIQ Protocol
          </span>
          <p className="text-on-surface-variant font-body-sm">
            © {new Date().getFullYear()} CarbonIQ Protocol. Decentralized
            Verification Layer.
          </p>
        </div>
        <div className="flex flex-wrap gap-8">
          <Link
            href="/docs"
            className="text-on-surface-variant font-body-sm hover:text-primary transition-colors"
          >
            Documentation
          </Link>
          <Link
            href="/methodology"
            className="text-on-surface-variant font-body-sm hover:text-primary transition-colors"
          >
            Whitepaper
          </Link>
        </div>
      </footer>
    </div>
  );
}
