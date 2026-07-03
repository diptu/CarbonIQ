import type { Metadata } from "next";
import { GlassCard } from "@/components/ui";

export const metadata: Metadata = {
  title: "Scope 2 Inventory & Analysis",
  description: "Real-time market-based emissions tracking with grid intensity signals.",
};

const OVERVIEW_CARDS = [
  {
    icon: "cloud",
    label: "Gross Scope 2 Emissions",
    value: "12,482",
    unit: "tCO2e",
    trend: "+4.2% from last period",
    trendColor: "text-error",
  },
  {
    icon: "energy_savings_leaf",
    label: "Net Market-Based Emissions",
    value: "2,105",
    unit: "tCO2e",
    trend: "83% reduction via RECs/PPAs",
    trendColor: "text-primary-fixed-dim",
    highlighted: true,
  },
  {
    icon: "bolt",
    label: "Avg. Grid Intensity",
    value: "0.42",
    unit: "kgCO2e/MWh",
    live: true,
  },
];

const ATTRIBUTION = [
  { label: "PPA Attribution", value: 42, color: "bg-primary-container" },
  { label: "Bundled RECs", value: 28, color: "bg-primary" },
  { label: "GreenPower", value: 13, color: "bg-primary-fixed" },
];

const INVENTORY_ROWS = [
  {
    name: "Tesla Giga Berlin",
    location: "Brandenburg, Germany",
    icon: "factory",
    period: "Q3 2024",
    consumption: "4,280 MWh",
    matchPct: "100%",
    netEmissions: "0.00 tCO2e",
    status: "Verified",
  },
  {
    name: "Amsterdam HQ",
    location: "North Holland, NL",
    icon: "apartment",
    period: "Q3 2024",
    consumption: "850 MWh",
    matchPct: "65%",
    netEmissions: "124.5 tCO2e",
    status: "Pending",
  },
  {
    name: "Sydney Data Center",
    location: "NSW, Australia",
    icon: "dns",
    period: "Q3 2024",
    consumption: "12,150 MWh",
    matchPct: "92%",
    netEmissions: "380.2 tCO2e",
    status: "Verified",
  },
];

export default function Scope2Page() {
  return (
    <div className="px-6 lg:px-12 py-10 max-w-7xl mx-auto">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-12">
        <div>
          <nav className="flex items-center gap-2 text-on-surface-variant font-label-sm text-label-sm mb-2 opacity-60">
            <span>Scope 2 Analysis</span>
            <span className="material-symbols-outlined text-[14px]">chevron_right</span>
            <span className="text-on-surface">Global Inventory</span>
          </nav>
          <h1 className="font-headline-xl text-headline-xl text-primary tracking-tight">
            Inventory &amp; Analysis
          </h1>
          <p className="text-on-surface-variant font-body-md max-w-2xl mt-2">
            Real-time market-based emissions tracking with integrated AEMO
            grid intensity signals and PPA attribution.
          </p>
        </div>
        <div className="flex items-center gap-4">
          <button className="flex items-center gap-2 px-5 py-3 rounded-xl bg-surface-variant/20 border border-white/10 text-on-surface font-label-md text-label-md hover:bg-surface-variant/40 transition-all">
            <span className="material-symbols-outlined text-[20px]">
              refresh
            </span>
            Recalculate Data
          </button>
          <button className="flex items-center gap-2 px-5 py-3 rounded-xl bg-primary-container text-on-primary-container font-label-md text-label-md font-bold active:scale-95 transition-all">
            <span className="material-symbols-outlined text-[20px]">
              ios_share
            </span>
            Export Audit Report
          </button>
        </div>
      </div>

      {/* Overview cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {OVERVIEW_CARDS.map((card) => (
          <GlassCard
            key={card.label}
            className={`p-6 relative overflow-hidden ${
              card.highlighted ? "border-primary/20 bg-primary/5" : ""
            }`}
          >
            <span
              className={`material-symbols-outlined absolute -right-4 -top-4 text-[120px] opacity-5 ${
                card.highlighted ? "opacity-10" : ""
              }`}
            >
              {card.icon}
            </span>
            <div className="flex justify-between items-start mb-4">
              <span
                className={`font-label-md text-label-md ${
                  card.highlighted ? "text-primary/80" : "text-on-surface-variant"
                }`}
              >
                {card.label}
              </span>
              {card.live && (
                <span className="bg-secondary/10 text-secondary text-[10px] px-2 py-0.5 rounded font-bold uppercase tracking-wider">
                  Live
                </span>
              )}
            </div>
            <div className="flex items-baseline gap-2">
              <span
                className={`font-headline-lg text-headline-lg ${
                  card.highlighted ? "text-primary-container" : "text-primary"
                }`}
              >
                {card.value}
              </span>
              <span className="font-label-md text-label-md text-on-surface-variant">
                {card.unit}
              </span>
            </div>
            {card.trend && (
              <div
                className={`mt-4 flex items-center gap-2 font-label-sm text-label-sm ${card.trendColor}`}
              >
                <span className="material-symbols-outlined text-[16px]">
                  {card.highlighted ? "verified" : "trending_up"}
                </span>
                {card.trend}
              </div>
            )}
          </GlassCard>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
        {/* Grid intensity chart */}
        <GlassCard className="lg:col-span-2 p-8 h-[420px] flex flex-col">
          <div className="flex items-center justify-between mb-10">
            <div>
              <h2 className="font-headline-md text-headline-md text-primary mb-1">
                Grid Intensity vs. Load
              </h2>
              <p className="text-on-surface-variant font-label-md">
                Hourly correlation of real-time operational load and grid
                carbon intensity.
              </p>
            </div>
          </div>
          <div className="flex-1 flex items-end gap-1 border-l border-b border-white/5">
            {Array.from({ length: 20 }).map((_, i) => (
              <div
                key={i}
                className="flex-1 flex flex-col justify-end items-center gap-1 h-full"
              >
                <div
                  className="w-full bg-secondary/20 rounded-t-sm hover:bg-secondary/40 transition-all"
                  style={{ height: `${20 + ((i * 13) % 60)}%` }}
                />
                <div
                  className="w-full bg-primary/40 rounded-t-sm hover:bg-primary/60 transition-all"
                  style={{ height: `${10 + ((i * 7) % 50)}%` }}
                />
              </div>
            ))}
          </div>
        </GlassCard>

        {/* Load attribution */}
        <GlassCard className="p-8 flex flex-col">
          <h2 className="font-headline-md text-headline-md text-primary mb-6">
            Load Attribution
          </h2>
          <div className="space-y-6 flex-1">
            {ATTRIBUTION.map((item) => (
              <div key={item.label}>
                <div className="flex justify-between items-center mb-2 font-label-md text-label-md">
                  <span className="text-on-surface">{item.label}</span>
                  <span className="text-primary">{item.value}%</span>
                </div>
                <div className="h-2 w-full bg-white/5 rounded-full overflow-hidden">
                  <div
                    className={`h-full ${item.color}`}
                    style={{ width: `${item.value}%` }}
                  />
                </div>
              </div>
            ))}
            <div className="mt-6 p-5 rounded-2xl bg-error/5 border border-error/20">
              <div className="flex items-center gap-3 mb-2">
                <span className="material-symbols-outlined text-error">
                  warning
                </span>
                <span className="font-label-md text-label-md text-error font-bold">
                  Residual Fossil Load
                </span>
              </div>
              <div className="flex items-baseline gap-2">
                <span className="text-2xl font-bold text-on-surface">
                  17%
                </span>
                <span className="text-on-surface-variant text-body-sm">
                  (1.4 GWh un-matched)
                </span>
              </div>
              <button className="mt-4 w-full py-2 bg-error text-on-error font-label-sm text-label-sm font-bold rounded-lg hover:bg-error/90 transition-colors">
                Buy Spot RECs
              </button>
            </div>
          </div>
        </GlassCard>
      </div>

      {/* Inventory table */}
      <GlassCard className="overflow-hidden">
        <div className="p-8 border-b border-white/5 flex items-center justify-between">
          <h2 className="font-headline-md text-headline-md text-primary">
            Emissions Inventory
          </h2>
          <span className="text-on-surface-variant text-[12px]">
            Showing 1-3 of 14 facilities
          </span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse min-w-[720px]">
            <thead className="bg-white/[0.02]">
              <tr className="text-on-surface-variant font-label-md text-label-md border-b border-white/5">
                <th className="px-8 py-5 font-medium">Emission Source</th>
                <th className="px-6 py-5 font-medium">Period</th>
                <th className="px-6 py-5 font-medium">Gross Consumption</th>
                <th className="px-6 py-5 font-medium">Renewables Match %</th>
                <th className="px-6 py-5 font-medium">Net Emissions</th>
                <th className="px-6 py-5 font-medium">Status</th>
              </tr>
            </thead>
            <tbody className="text-body-sm text-on-surface divide-y divide-white/[0.03]">
              {INVENTORY_ROWS.map((row) => (
                <tr
                  key={row.name}
                  className="hover:bg-white/[0.02] transition-colors"
                >
                  <td className="px-8 py-5">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-surface-variant flex items-center justify-center">
                        <span className="material-symbols-outlined text-[18px] text-primary">
                          {row.icon}
                        </span>
                      </div>
                      <div>
                        <div className="font-bold">{row.name}</div>
                        <div className="text-[11px] text-on-surface-variant">
                          {row.location}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-5 font-mono text-[13px]">
                    {row.period}
                  </td>
                  <td className="px-6 py-5 font-medium">
                    {row.consumption}
                  </td>
                  <td className="px-6 py-5 text-primary">{row.matchPct}</td>
                  <td className="px-6 py-5">{row.netEmissions}</td>
                  <td className="px-6 py-5">
                    <span
                      className={`px-2.5 py-1 rounded-full text-[11px] font-bold uppercase tracking-wider flex items-center gap-1 w-fit border ${
                        row.status === "Verified"
                          ? "bg-primary/10 text-primary-fixed-dim border-primary/20"
                          : "bg-secondary/10 text-secondary border-secondary/20"
                      }`}
                    >
                      <span
                        className={`w-1 h-1 rounded-full ${
                          row.status === "Verified"
                            ? "bg-primary-container"
                            : "bg-secondary-container animate-pulse"
                        }`}
                      />
                      {row.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </GlassCard>
    </div>
  );
}
