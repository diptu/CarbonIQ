import type { Metadata } from "next";
import { GlassCard } from "@/components/ui";
import { ProtocolSidebar } from "@/components/protocol/ProtocolSidebar";

export const metadata: Metadata = {
  title: "Smart Contracts",
  description: "Manage and interact with the CarbonIQ Protocol's decentralized infrastructure.",
};

const CONTRACTS = [
  { icon: "gavel", iconClass: "bg-primary-container/20 text-primary-container", name: "Verification Engine", version: "v2.4.1", address: "0x71C...93A2" },
  { icon: "database", iconClass: "bg-secondary/20 text-secondary", name: "Credit Registry", version: "v1.1.0", address: "0x4F2...E881" },
  { icon: "groups", iconClass: "bg-tertiary-container/20 text-tertiary-container", name: "Governance DAO", version: "v3.0.0", address: "0xBE9...77C0" },
  { icon: "sensors", iconClass: "bg-primary-fixed-dim/20 text-primary-fixed-dim", name: "Oracle Manager", version: "v1.2.4", address: "0x0A1...DD44" },
];

const FUNCTIONS = [
  { name: "getVerificationStatus", type: "view", input: "assetID (uint256)", cta: "Execute Query" },
  { name: "totalSupply", type: "view", description: "Returns the current total supply of Carbon Credits circulating on-chain.", cta: "Query" },
  { name: "getProjectOracleData", type: "view", input: "projectAddress (address)", cta: "Fetch Data" },
];

const HISTORY = [
  { time: "Oct 24, 2023 • 14:22", title: "Proxy Upgrade: Verification Engine", detail: "Implementation updated to v2.4.1. Optimized gas costs for multi-asset verification by 12%.", tx: "0x98f2...1a23", color: "border-primary-container" },
  { time: "Oct 12, 2023 • 09:15", title: "Parameter Changed: Registry Fee", detail: "DAO Governance Vote #82: Reduced verification fee from 0.05 ETH to 0.035 ETH.", tx: "0x42e1...bb90", color: "border-secondary" },
  { time: "Sep 28, 2023 • 22:45", title: "Contract Deployed: Oracle Manager", detail: "Genesis deployment of the decentralized Oracle aggregator for environmental satellite data.", tx: "0x11c7...44d2", color: "border-tertiary-container" },
  { time: "Sep 15, 2023 • 11:00", title: "Audit Completion", detail: "CertiK finalized the core protocol security audit. Total score: 98/100.", color: "border-outline-variant", muted: true },
];

export default function SmartContractsPage() {
  return (
    <div className="min-h-screen">
      <ProtocolSidebar />
      <main className="lg:ml-64 p-6 md:p-margin-desktop min-h-screen">
        <header className="flex flex-col md:flex-row justify-between md:items-end gap-6 mb-12">
          <div>
            <h1 className="font-headline-xl text-headline-xl text-primary-fixed-dim mb-2">
              Smart Contracts
            </h1>
            <p className="text-on-surface-variant text-body-lg max-w-2xl">
              Manage and interact with the CarbonIQ Protocol&apos;s
              decentralized infrastructure. Securely monitor verification
              engines and credit registries on-chain.
            </p>
          </div>
          <button className="bg-primary-container text-on-primary-container px-6 py-3 rounded-full font-label-md text-label-md hover:scale-105 transition-transform duration-150 flex items-center gap-2 shrink-0">
            <span className="material-symbols-outlined text-[20px]">
              account_balance_wallet
            </span>
            Connect Wallet
          </button>
        </header>

        <section className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-12">
          {CONTRACTS.map((contract) => (
            <GlassCard key={contract.name} className="p-6 relative overflow-hidden">
              <div className="flex justify-between items-start">
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-lg ${contract.iconClass}`}>
                    <span className="material-symbols-outlined">
                      {contract.icon}
                    </span>
                  </div>
                  <h3 className="font-headline-md text-headline-md">
                    {contract.name}
                  </h3>
                </div>
                <span className="bg-surface-container-highest text-primary-fixed-dim text-xs px-2 py-1 rounded border border-primary-fixed-dim/20">
                  {contract.version}
                </span>
              </div>
              <div className="space-y-3 mt-4">
                <div className="flex items-center justify-between p-3 bg-black/20 rounded-xl">
                  <code className="text-sm font-mono text-on-surface-variant">
                    {contract.address}
                  </code>
                  <span className="material-symbols-outlined text-[18px] hover:text-primary-container transition-colors cursor-pointer">
                    content_copy
                  </span>
                </div>
                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-1.5 text-secondary">
                    <span className="material-symbols-outlined text-[16px]">
                      shield_lock
                    </span>
                    <span className="text-xs font-label-sm">
                      Audited by CertiK
                    </span>
                  </div>
                  <span className="flex items-center gap-1.5 text-on-surface-variant hover:text-primary-fixed-dim transition-colors cursor-pointer">
                    <span className="material-symbols-outlined text-[16px]">
                      open_in_new
                    </span>
                    <span className="text-xs font-label-sm">
                      View on Explorer
                    </span>
                  </span>
                </div>
              </div>
            </GlassCard>
          ))}
        </section>

        <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
          <div className="xl:col-span-2 flex flex-col gap-6">
            <GlassCard className="p-8">
              <div className="flex items-center justify-between mb-8">
                <div className="flex items-center gap-3">
                  <span className="material-symbols-outlined text-primary-container">
                    terminal
                  </span>
                  <h2 className="font-headline-md text-headline-md">
                    Function Explorer
                  </h2>
                </div>
                <div className="flex bg-black/20 p-1 rounded-lg">
                  <button className="px-4 py-1.5 rounded-md bg-primary-container text-on-primary-container text-label-md font-label-md">
                    Read
                  </button>
                  <button className="px-4 py-1.5 rounded-md text-on-surface-variant hover:text-primary-container transition-colors text-label-md font-label-md">
                    Write
                  </button>
                </div>
              </div>
              <div className="space-y-4">
                {FUNCTIONS.map((fn) => (
                  <details
                    key={fn.name}
                    className="group bg-surface-container-low border border-outline-variant/30 rounded-2xl transition-all"
                  >
                    <summary className="flex items-center justify-between p-4 cursor-pointer list-none">
                      <div className="flex items-center gap-4">
                        <span className="font-mono text-primary-container">
                          {fn.name}
                        </span>
                        <span className="text-xs text-on-surface-variant font-label-sm opacity-50 px-2 py-0.5 border border-outline-variant/30 rounded">
                          {fn.type}
                        </span>
                      </div>
                      <span className="material-symbols-outlined group-open:rotate-180 transition-transform">
                        expand_more
                      </span>
                    </summary>
                    <div className="px-4 pb-4 border-t border-outline-variant/30 pt-4">
                      {fn.description ? (
                        <div className="flex items-center justify-between gap-4">
                          <p className="text-sm text-on-surface-variant">
                            {fn.description}
                          </p>
                          <button className="bg-surface-container-high text-primary-fixed-dim px-6 h-10 rounded-xl font-label-md text-sm border border-primary-fixed-dim/20 hover:bg-primary-container hover:text-on-primary-container transition-all shrink-0">
                            {fn.cta}
                          </button>
                        </div>
                      ) : (
                        <div className="space-y-4">
                          <input
                            className="w-full bg-black/20 border border-outline-variant/30 rounded-xl px-4 py-2 text-sm focus:ring-1 focus:ring-primary-container outline-none transition-all"
                            placeholder={fn.input}
                            type="text"
                          />
                          <button className="w-full h-10 bg-surface-container-high text-primary-fixed-dim rounded-xl font-label-md text-sm border border-primary-fixed-dim/20 hover:bg-primary-container hover:text-on-primary-container transition-all">
                            {fn.cta}
                          </button>
                        </div>
                      )}
                    </div>
                  </details>
                ))}
              </div>
            </GlassCard>

            <GlassCard className="p-8 overflow-hidden">
              <div className="flex items-center gap-3 mb-6">
                <span className="material-symbols-outlined text-secondary">
                  integration_instructions
                </span>
                <h2 className="font-headline-md text-headline-md">
                  Integration Snippets
                </h2>
              </div>
              <div className="bg-black/30 p-6 rounded-2xl border border-outline-variant/20 font-mono">
                <div className="flex items-center gap-4 mb-4 pb-2 border-b border-outline-variant/10 text-xs">
                  <span className="text-primary-container border-b border-primary-container pb-2">
                    JavaScript
                  </span>
                  <span className="text-on-surface-variant pb-2">Python</span>
                  <span className="text-on-surface-variant pb-2">
                    Solidity
                  </span>
                </div>
                <pre className="text-sm leading-relaxed overflow-x-auto text-on-surface-variant whitespace-pre-wrap">
{`const { CarbonIQSDK } = require('@carboniq/core');

async function getVerification(assetId) {
  const sdk = new CarbonIQSDK({ network: 'mainnet' });
  const result = await sdk.contracts.engine.call('getVerificationStatus', [assetId]);

  console.log(\`Asset \${assetId} status: \${result}\`);
}`}
                </pre>
              </div>
            </GlassCard>
          </div>

          <GlassCard className="p-8">
            <div className="flex items-center gap-3 mb-8">
              <span className="material-symbols-outlined text-tertiary-container">
                history
              </span>
              <h2 className="font-headline-md text-headline-md">History</h2>
            </div>
            <div className="relative space-y-8 before:absolute before:left-[11px] before:top-2 before:bottom-0 before:w-0.5 before:bg-outline-variant/30">
              {HISTORY.map((event) => (
                <div
                  key={event.title}
                  className={`relative pl-8 ${event.muted ? "opacity-60" : ""}`}
                >
                  <div
                    className={`absolute left-0 top-1.5 w-6 h-6 rounded-full bg-surface-container border-2 ${event.color} flex items-center justify-center`}
                  >
                    <div className="w-1.5 h-1.5 rounded-full bg-current" />
                  </div>
                  <div className="flex flex-col gap-1">
                    <p className="text-xs text-on-surface-variant font-label-sm uppercase tracking-wider">
                      {event.time}
                    </p>
                    <h4 className="text-body-md font-semibold text-primary">
                      {event.title}
                    </h4>
                    <p className="text-sm text-on-surface-variant">
                      {event.detail}
                    </p>
                    {event.tx && (
                      <span className="text-xs text-primary-fixed-dim hover:underline flex items-center gap-1 mt-1 cursor-pointer">
                        TX: {event.tx}{" "}
                        <span className="material-symbols-outlined text-[12px]">
                          open_in_new
                        </span>
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
            <button className="w-full mt-10 py-3 border border-outline-variant/30 rounded-xl text-on-surface-variant hover:bg-surface-container-high transition-colors text-label-md font-label-md">
              View Full History
            </button>
          </GlassCard>
        </div>
      </main>
    </div>
  );
}
