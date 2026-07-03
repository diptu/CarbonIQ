import type { Metadata } from "next";
import { GlassCard } from "@/components/ui";

export const metadata: Metadata = {
  title: "API & Security Console",
  description: "Manage authentication layers and data sovereignty controls.",
};

const API_KEYS = [
  { icon: "hub", iconClass: "bg-primary/10 text-primary-container", name: "Production Ingestion Hub", key: "ck_live_•••••••••••••••••••••4829", quota: 65 },
  { icon: "terminal", iconClass: "bg-secondary/10 text-secondary", name: "Development Staging Environ", key: "ck_test_•••••••••••••••••••••9102", quota: 12 },
  { icon: "link_off", iconClass: "bg-surface-container-highest text-on-surface-variant", name: "Legacy Sensor Node-04", key: "ck_expired_•••••••••••••••••••••2201", revoked: true },
];

const TOGGLES = [
  { label: "MFA Enforcement", note: "Require 2FA for all admin roles.", checked: true },
  { label: "IP Whitelisting", note: "Restrict access to verified CIDRs.", checked: false },
];

const WEBHOOKS = [
  { event: "Verification Completed", url: "https://api.veritas.io/hooks/carbon", status: "Active" },
  { event: "Credit Minted", url: "https://ledger-sync.net/v2/update", status: "Active" },
  { event: "Security Alert", url: "https://security.carboniq.com/notify", status: "Failing (500)" },
];

export default function ApiSecurityPage() {
  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto w-full">
      <div className="mb-10">
        <div className="flex items-center gap-2 text-primary-container mb-2">
          <span className="material-symbols-outlined text-sm">security</span>
          <span className="font-label-md text-label-md tracking-widest uppercase">
            System Security Architecture
          </span>
        </div>
        <h1 className="font-headline-xl text-headline-xl text-primary">
          API &amp; Security Protocols
        </h1>
        <p className="text-on-surface-variant mt-2 max-w-2xl">
          Manage high-integrity data pipelines, authentication layers, and
          geographic data sovereignty controls for the CarbonIQ ledger.
        </p>
      </div>

      <div className="grid grid-cols-12 gap-gutter">
        <GlassCard className="col-span-12 lg:col-span-8 p-8 flex flex-col">
          <div className="flex justify-between items-start mb-8">
            <div>
              <h3 className="font-headline-md text-headline-md text-primary">
                API Key Management
              </h3>
              <p className="text-on-surface-variant text-sm mt-1">
                Active integration credentials and throughput quotas.
              </p>
            </div>
            <button className="bg-primary-container text-on-primary-container font-bold px-6 py-3 rounded-xl neon-glow hover:scale-[1.02] active:scale-95 transition-all flex items-center gap-2">
              <span className="material-symbols-outlined">add</span>
              Generate New Key
            </button>
          </div>
          <div className="space-y-4">
            {API_KEYS.map((key) => (
              <div
                key={key.name}
                className={`bg-surface-container/50 border border-outline-variant p-5 rounded-xl flex items-center justify-between hover:bg-surface-container-high transition-colors ${
                  key.revoked ? "opacity-60" : ""
                }`}
              >
                <div className="flex gap-4">
                  <div
                    className={`w-12 h-12 rounded-lg flex items-center justify-center ${key.iconClass}`}
                  >
                    <span className="material-symbols-outlined">
                      {key.icon}
                    </span>
                  </div>
                  <div>
                    <h4 className="font-bold text-primary">{key.name}</h4>
                    <p className="font-mono text-sm text-on-surface-variant mt-1">
                      {key.key}
                    </p>
                  </div>
                </div>
                {key.revoked ? (
                  <span className="bg-surface-container-highest text-on-surface-variant text-[10px] px-3 py-1 rounded-full uppercase font-bold">
                    Revoked
                  </span>
                ) : (
                  <div className="text-right flex items-center gap-8">
                    <div>
                      <p className="text-[10px] text-on-surface-variant uppercase tracking-widest">
                        Usage Quota
                      </p>
                      <div className="flex items-center gap-3 mt-1">
                        <div className="w-24 h-1.5 bg-surface-container-highest rounded-full overflow-hidden">
                          <div
                            className="h-full bg-primary-container"
                            style={{ width: `${key.quota}%` }}
                          />
                        </div>
                        <span className="text-xs font-mono">
                          {key.quota}%
                        </span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </GlassCard>

        <GlassCard className="col-span-12 lg:col-span-4 p-8">
          <h3 className="font-headline-md text-headline-md text-primary mb-6">
            Security Protocols
          </h3>
          <div className="space-y-6">
            {TOGGLES.map((toggle) => (
              <div key={toggle.label} className="flex items-center justify-between">
                <div>
                  <h4 className="font-bold text-primary">{toggle.label}</h4>
                  <p className="text-xs text-on-surface-variant">
                    {toggle.note}
                  </p>
                </div>
                <div
                  className={`w-11 h-6 rounded-full relative ${
                    toggle.checked
                      ? "bg-primary-container"
                      : "bg-surface-container-highest"
                  }`}
                >
                  <div
                    className={`absolute top-[2px] w-5 h-5 bg-white rounded-full transition-all ${
                      toggle.checked ? "left-[22px]" : "left-[2px]"
                    }`}
                  />
                </div>
              </div>
            ))}
            <hr className="border-outline-variant/30" />
            <div>
              <div className="flex justify-between items-center mb-4">
                <h4 className="font-bold text-primary">JWT Rotation</h4>
                <span className="text-xs text-primary-container font-mono bg-primary/10 px-2 py-0.5 rounded">
                  Every 24 Hours
                </span>
              </div>
              <input
                className="w-full h-1.5 bg-surface-container-highest rounded-lg appearance-none cursor-pointer accent-primary-container"
                type="range"
                defaultValue={50}
              />
              <div className="flex justify-between text-[10px] text-on-surface-variant mt-2 uppercase tracking-widest font-bold">
                <span>1h</span>
                <span>12h</span>
                <span>24h</span>
                <span>7d</span>
              </div>
            </div>
            <div className="bg-primary/5 border border-primary-container/20 p-4 rounded-xl">
              <div className="flex gap-3">
                <span className="material-symbols-outlined text-primary-container">
                  info
                </span>
                <p className="text-xs text-on-surface-variant leading-relaxed">
                  System health is{" "}
                  <span className="text-primary-container font-bold">
                    Optimal
                  </span>
                  . All active sessions are verified with hardware-backed
                  keys.
                </p>
              </div>
            </div>
          </div>
        </GlassCard>

        <GlassCard className="col-span-12 lg:col-span-7 p-8">
          <h3 className="font-headline-md text-headline-md text-primary mb-1">
            Webhooks Configuration
          </h3>
          <p className="text-on-surface-variant text-sm mb-8">
            Real-time event notifications for your infrastructure.
          </p>
          <div className="overflow-x-auto">
            <table className="w-full text-left min-w-[480px]">
              <thead className="text-xs uppercase tracking-widest text-on-surface-variant border-b border-outline-variant">
                <tr>
                  <th className="pb-4 font-semibold">Event Type</th>
                  <th className="pb-4 font-semibold">Endpoint URL</th>
                  <th className="pb-4 font-semibold">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-outline-variant/30">
                {WEBHOOKS.map((hook) => (
                  <tr key={hook.event}>
                    <td className="py-5">
                      <span className="font-bold text-primary">
                        {hook.event}
                      </span>
                    </td>
                    <td className="py-5">
                      <span className="font-mono text-xs text-on-surface-variant">
                        {hook.url}
                      </span>
                    </td>
                    <td className="py-5">
                      <span
                        className={`flex items-center gap-1.5 text-xs font-bold ${
                          hook.status === "Active"
                            ? "text-primary-container"
                            : "text-error"
                        }`}
                      >
                        <span
                          className={`w-1.5 h-1.5 rounded-full ${
                            hook.status === "Active"
                              ? "bg-primary-container animate-pulse"
                              : "bg-error"
                          }`}
                        />
                        {hook.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </GlassCard>

        <GlassCard className="col-span-12 lg:col-span-5 p-8 relative overflow-hidden">
          <h3 className="font-headline-md text-headline-md text-primary mb-2">
            Data Privacy &amp; Sovereignty
          </h3>
          <p className="text-on-surface-variant text-sm mb-8">
            Manage regional data residency and PII compliance.
          </p>
          <div className="space-y-6 relative z-10">
            <div>
              <label className="block text-xs font-bold text-on-surface-variant uppercase tracking-widest mb-3">
                Primary Data Residency
              </label>
              <select className="w-full bg-surface-container border border-outline-variant rounded-xl py-3 px-4 text-primary appearance-none focus:ring-1 focus:ring-primary-container">
                <option>Store all PII in EU-West-1 (Ireland)</option>
                <option>US-East-1 (North Virginia)</option>
                <option>AP-Southeast-2 (Sydney)</option>
              </select>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="p-4 rounded-xl bg-surface-container border border-outline-variant">
                <h5 className="text-xs font-bold text-secondary uppercase mb-1">
                  GDPR Status
                </h5>
                <p className="text-primary font-bold">Compliant</p>
              </div>
              <div className="p-4 rounded-xl bg-surface-container border border-outline-variant">
                <h5 className="text-xs font-bold text-tertiary-fixed-dim uppercase mb-1">
                  CCPA Status
                </h5>
                <p className="text-primary font-bold">Compliant</p>
              </div>
            </div>
            <button className="w-full bg-surface-container-highest border border-outline-variant hover:border-primary-container text-primary font-bold py-3 rounded-xl transition-all">
              Request Data Export
            </button>
          </div>
        </GlassCard>
      </div>
    </div>
  );
}
