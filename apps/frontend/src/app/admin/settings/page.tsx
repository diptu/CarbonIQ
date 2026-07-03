import type { Metadata } from "next";
import { GlassCard } from "@/components/ui";

export const metadata: Metadata = {
  title: "System Settings",
  description: "Configure the microservice environment and integration handshakes.",
};

const HEALTH_WIDGETS = [
  { icon: "verified", label: "Microservice Health", value: "99.98% Uptime", detail: "Latency: 42ms", color: "border-primary-fixed-dim/20 text-primary-fixed-dim" },
  { icon: "history", label: "Schema Version", value: "v2.4.1 (Stable LTS)", detail: "Released 2 days ago", color: "border-secondary-container/20 text-secondary-container" },
  { icon: "security", label: "Encryption", value: "AES-256 GCM Protocol", detail: "MIL-SPEC", color: "border-tertiary-fixed-dim/20 text-tertiary-fixed-dim" },
];

export default function AdminSettingsPage() {
  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto w-full">
      <div className="flex justify-between items-end mb-8 flex-wrap gap-4">
        <div>
          <h1 className="font-headline-xl text-headline-xl text-primary-fixed-dim mb-2">
            System Settings &amp; Configuration
          </h1>
          <p className="text-on-surface-variant">
            Manage your microservice environment and integration
            handshakes.
          </p>
        </div>
        <div className="flex gap-4">
          <button className="px-6 py-2 border border-white/10 rounded-full text-label-md font-label-md hover:border-primary-fixed-dim/40 transition-all text-on-surface-variant">
            Export Config
          </button>
          <button className="px-6 py-2 bg-primary-fixed-dim text-on-primary-fixed font-bold rounded-full text-label-md font-label-md">
            Commit Updates
          </button>
        </div>
      </div>

      <div className="grid grid-cols-12 gap-gutter">
        <GlassCard className="col-span-12 lg:col-span-4 p-8 flex flex-col gap-8">
          <div className="flex items-center gap-3">
            <span className="material-symbols-outlined text-primary-fixed-dim">
              tune
            </span>
            <h3 className="font-headline-md text-headline-md">
              Global Preferences
            </h3>
          </div>
          <div className="space-y-3">
            <label className="font-label-md text-label-md text-on-surface-variant block uppercase tracking-widest">
              Unit System
            </label>
            <div className="flex bg-surface-container-lowest p-1 rounded-lg border border-white/10">
              <button className="flex-1 py-2 font-label-md text-label-md rounded bg-primary-fixed-dim text-on-primary-fixed">
                Metric
              </button>
              <button className="flex-1 py-2 font-label-md text-label-md text-on-surface-variant hover:text-on-surface transition-colors">
                Imperial
              </button>
            </div>
          </div>
          <div className="space-y-3">
            <label className="font-label-md text-label-md text-on-surface-variant block uppercase tracking-widest">
              Base Currency
            </label>
            <select className="w-full bg-surface-container-lowest border border-white/10 text-on-surface font-body-md text-body-md px-4 py-3 rounded-lg focus:outline-none focus:border-primary-fixed-dim transition-colors appearance-none">
              <option value="USD">USD - US Dollar ($)</option>
              <option value="EUR">EUR - Euro (€)</option>
              <option value="GBP">GBP - British Pound (£)</option>
              <option value="JPY">JPY - Japanese Yen (¥)</option>
            </select>
          </div>
          <div className="space-y-3">
            <div className="flex justify-between items-end">
              <label className="font-label-md text-label-md text-on-surface-variant uppercase tracking-widest">
                Decimal Precision
              </label>
              <span className="font-headline-md text-primary-fixed-dim">
                4
              </span>
            </div>
            <input
              className="w-full h-1 bg-surface-container-highest rounded-lg appearance-none cursor-pointer accent-primary-fixed-dim"
              max={8}
              min={0}
              type="range"
              defaultValue={4}
            />
            <div className="flex justify-between text-[10px] text-on-surface-variant/50 font-label-sm uppercase">
              <span>Coarse</span>
              <span>High Precision</span>
            </div>
          </div>
        </GlassCard>

        <GlassCard className="col-span-12 lg:col-span-8 p-8 flex flex-col gap-8">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-3">
              <span className="material-symbols-outlined text-primary-fixed-dim">
                hub
              </span>
              <h3 className="font-headline-md text-headline-md">
                Integration Tokens
              </h3>
            </div>
            <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-primary-fixed-dim/10 border border-primary-fixed-dim/20">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary-fixed-dim opacity-75" />
                <span className="relative inline-flex rounded-full h-2 w-2 bg-primary-fixed-dim" />
              </span>
              <span className="font-label-sm text-label-sm text-primary-fixed-dim">
                Connection: Active
              </span>
            </div>
          </div>
          <div className="space-y-3">
            <label className="font-label-md text-label-md text-on-surface-variant block uppercase tracking-widest">
              Production API Key
            </label>
            <div className="flex flex-col sm:flex-row gap-3">
              <div className="flex-1 bg-surface-container-lowest border border-white/10 rounded-lg px-4 py-3 font-mono text-sm flex items-center justify-between text-on-surface-variant">
                <span>ecolens_prod_••••••••••••••••••••3a9c</span>
                <span className="material-symbols-outlined text-primary-fixed-dim/50 scale-75">
                  lock
                </span>
              </div>
              <button className="px-4 py-2 border border-white/10 rounded-lg hover:border-primary-fixed-dim/50 hover:text-primary-fixed-dim transition-all flex items-center gap-2 font-label-md">
                <span className="material-symbols-outlined text-lg">
                  content_copy
                </span>
                Copy
              </button>
              <button className="px-4 py-2 border border-white/10 rounded-lg hover:border-error/50 hover:text-error transition-all flex items-center gap-2 font-label-md">
                <span className="material-symbols-outlined text-lg">
                  refresh
                </span>
                Rotate
              </button>
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-3">
              <label className="font-label-md text-label-md text-on-surface-variant block uppercase tracking-widest">
                Endpoint URL
              </label>
              <div className="w-full bg-surface-container-lowest border border-white/10 px-4 py-3 rounded-lg font-mono text-sm text-on-surface-variant overflow-hidden whitespace-nowrap">
                https://api.carboniq.io/v2/stream/ingest
              </div>
            </div>
            <div className="space-y-3">
              <label className="font-label-md text-label-md text-on-surface-variant block uppercase tracking-widest">
                Secret Hash
              </label>
              <div className="w-full bg-surface-container-lowest border border-white/10 px-4 py-3 rounded-lg font-mono text-sm text-on-surface-variant flex items-center justify-between">
                <span>sha256:7f8e9a...d2c1b0</span>
                <span className="material-symbols-outlined text-primary-fixed-dim/60 text-lg cursor-pointer">
                  visibility
                </span>
              </div>
            </div>
          </div>
          <div className="p-4 rounded bg-surface-container-low border-l-4 border-primary-fixed-dim">
            <p className="font-body-sm text-body-sm text-on-surface-variant italic">
              &quot;The &apos;Handshake&apos; protocol ensures that data
              frames sent to CarbonIQ are encrypted using SHA-256 HMAC
              signatures. Please keep your Secret Hash private.&quot;
            </p>
          </div>
        </GlassCard>

        <div className="col-span-12 grid grid-cols-1 md:grid-cols-3 gap-gutter">
          {HEALTH_WIDGETS.map((widget) => (
            <GlassCard key={widget.label} className="p-6 flex items-center gap-6">
              <div
                className={`w-16 h-16 rounded-full border-4 flex items-center justify-center ${widget.color}`}
              >
                <span className="material-symbols-outlined text-3xl">
                  {widget.icon}
                </span>
              </div>
              <div>
                <h4 className="font-label-md text-label-md text-on-surface">
                  {widget.label}
                </h4>
                <p className="text-xs text-on-surface-variant mt-1">
                  {widget.value}
                </p>
                <p className="text-[10px] text-on-surface-variant/60 uppercase font-bold mt-1 tracking-widest">
                  {widget.detail}
                </p>
              </div>
            </GlassCard>
          ))}
        </div>
      </div>
    </div>
  );
}
