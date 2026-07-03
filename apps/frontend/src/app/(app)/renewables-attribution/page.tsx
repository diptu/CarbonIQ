import type { Metadata } from "next";
import { GlassCard } from "@/components/ui";

export const metadata: Metadata = {
  title: "Renewables Attribution",
  description: "Match renewable energy certificates against site consumption.",
};

const KPIS = [
  { icon: "data_usage", label: "Total Consumption", value: "12,482", unit: "MWh" },
  { icon: "check_circle", label: "Matched Renewables", value: "84.2", unit: "%", highlighted: true, trend: "+5.4% from last month" },
  { icon: "warning", label: "Unmatched Load", value: "1,972", unit: "MWh" },
  { icon: "cloud_done", label: "Net Emissions", value: "482", unit: "tCO2e", note: "Market-based method" },
];

const FACILITIES = [
  { name: "OSL-01 Data Center", location: "Oslo, Norway", matched: "0% Matched", load: "Load: 4,500 MWh", accent: false },
  { name: "SFO-Hub Terminal", location: "California, USA", matched: "42% Matched", load: "Remaining: 1,200 MWh", accent: true },
  { name: "TYO-Logistics", location: "Tokyo, JP", matched: "12% Matched", load: "Remaining: 840 MWh", accent: false },
];

const ASSETS = [
  { icon: "wb_sunny", id: "RE-9021", vintage: "V-2023", name: "Solar Farm Alpha", location: "Spain (ES)", qty: "2,400 MWh" },
  { icon: "air", id: "WD-4481", vintage: "V-2023", name: "North Sea Wind II", location: "Norway (NO)", qty: "5,000 MWh" },
  { icon: "water_drop", id: "HY-2100", vintage: "V-2024", name: "Gorge Hydro Station", location: "Canada (CA)", qty: "1,150 MWh" },
];

const LEDGER_ROWS = [
  { txId: "#TRX-94821", facility: "SFO-Hub Terminal", instrument: "REC (Solar)", icon: "verified", vintage: "2023 Q4", qty: "1,500.00", status: "MATCHED" },
  { txId: "#TRX-94822", facility: "OSL-01 Data Center", instrument: "PPA (Wind)", icon: "description", vintage: "2024 Q1", qty: "3,250.00", status: "PENDING" },
  { txId: "#TRX-94823", facility: "TYO-Logistics", instrument: "GreenPower", icon: "shield_with_heart", vintage: "2023 Q3", qty: "850.00", status: "MATCHED" },
];

export default function RenewablesAttributionPage() {
  return (
    <div className="px-6 lg:px-12 py-10 max-w-7xl mx-auto space-y-10">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
        <div>
          <h1 className="font-headline-xl text-headline-xl text-primary leading-tight">
            Renewables Attribution
          </h1>
          <p className="font-body-md text-body-md text-on-surface-variant mt-2">
            Manage and match renewable energy certificates against site
            consumption across your global portfolio.
          </p>
        </div>
        <div className="flex items-center gap-3 px-4 py-2 bg-surface-container-high/40 border border-primary/20 rounded-full">
          <span className="w-2 h-2 rounded-full bg-primary-container animate-pulse" />
          <span className="text-sm font-medium text-primary">
            GHG Protocol Compliance:{" "}
            <span className="text-primary-container">Verified</span>
          </span>
        </div>
      </div>

      {/* KPI cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-gutter">
        {KPIS.map((kpi) => (
          <GlassCard
            key={kpi.label}
            className={`p-6 ${kpi.highlighted ? "border-primary-container neon-glow" : ""}`}
          >
            <div className="flex items-center justify-between mb-4">
              <span className="text-on-surface-variant text-sm font-medium">
                {kpi.label}
              </span>
              <span
                className={`material-symbols-outlined ${
                  kpi.highlighted
                    ? "text-primary-container"
                    : "text-on-surface-variant opacity-50"
                }`}
              >
                {kpi.icon}
              </span>
            </div>
            <div className="flex items-baseline gap-2">
              <span
                className={`font-headline-lg text-headline-lg ${
                  kpi.highlighted ? "text-primary-container" : "text-primary"
                }`}
              >
                {kpi.value}
              </span>
              <span className="text-on-surface-variant text-xs font-bold uppercase tracking-widest">
                {kpi.unit}
              </span>
            </div>
            {kpi.trend && (
              <p className="text-xs text-primary-container mt-4">
                {kpi.trend}
              </p>
            )}
            {kpi.note && (
              <p className="text-xs text-on-surface-variant mt-4">
                {kpi.note}
              </p>
            )}
          </GlassCard>
        ))}
      </div>

      <div className="grid grid-cols-12 gap-gutter items-start">
        {/* Net zero gap chart */}
        <GlassCard className="col-span-12 lg:col-span-4 p-8">
          <h3 className="font-headline-md text-headline-md text-primary mb-2">
            Net Zero Gap
          </h3>
          <p className="text-on-surface-variant text-sm mb-8">
            Visualization of hourly load matching vs grid emissions factor.
          </p>
          <div className="relative h-64 w-full flex items-end gap-1 px-2 border-l border-b border-white/10">
            {[80, 60, 100, 83, 66, 83, 80].map((h, i) => {
              const isError = i === 2 || i === 5;
              return (
                <div
                  key={i}
                  className={`flex-1 relative border-t ${
                    isError
                      ? "bg-error/20 border-error"
                      : "bg-primary-container/20 border-primary-container"
                  }`}
                  style={{ height: `${h}%` }}
                >
                  <div
                    className={`absolute bottom-0 w-full opacity-60 ${
                      isError ? "bg-error h-1/4" : "bg-primary-container h-1/2"
                    }`}
                  />
                </div>
              );
            })}
          </div>
          <div className="mt-8 space-y-4">
            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-sm bg-primary-container" />
                <span className="text-on-surface-variant">
                  Attributed Renewables
                </span>
              </div>
              <span className="text-primary font-bold">10,510 MWh</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-sm bg-error opacity-60" />
                <span className="text-on-surface-variant">
                  Fossil Fuel Load
                </span>
              </div>
              <span className="text-primary font-bold">1,972 MWh</span>
            </div>
          </div>
          <button className="w-full mt-8 py-3 bg-white/5 border border-white/10 rounded-xl text-sm font-medium hover:bg-white/10 transition-all">
            Download Detailed Gap Report
          </button>
        </GlassCard>

        {/* Matching workspace */}
        <div className="col-span-12 lg:col-span-8">
          <GlassCard className="overflow-hidden">
            <div className="p-6 border-b border-white/10 flex justify-between items-center bg-white/[0.02]">
              <h3 className="font-headline-md text-headline-md text-primary">
                Inventory Matching Engine
              </h3>
              <div className="flex gap-2">
                <button className="px-4 py-1.5 bg-surface-container-highest text-xs font-bold rounded-lg hover:bg-white/10">
                  Filter Assets
                </button>
                <button className="px-4 py-1.5 bg-primary-container text-on-primary-container text-xs font-bold rounded-lg">
                  Auto-Match (AI)
                </button>
              </div>
            </div>
            <div className="flex flex-col md:flex-row">
              {/* Facilities */}
              <div className="w-full md:w-1/2 border-r border-white/10">
                <div className="p-4 bg-white/5 flex items-center justify-between">
                  <span className="text-xs font-bold text-on-surface-variant uppercase tracking-widest">
                    Unmatched Facilities
                  </span>
                  <span className="bg-surface-container text-[10px] px-2 py-0.5 rounded text-on-surface-variant">
                    14 Pending
                  </span>
                </div>
                <div className="p-2 space-y-2">
                  {FACILITIES.map((facility) => (
                    <div
                      key={facility.name}
                      className={`p-4 rounded-xl border border-white/5 bg-white/[0.02] hover:border-primary/40 cursor-pointer transition-all ${
                        facility.accent ? "border-l-4 border-l-secondary-container" : ""
                      }`}
                    >
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <p className="text-sm font-bold text-primary">
                            {facility.name}
                          </p>
                          <p className="text-xs text-on-surface-variant">
                            {facility.location}
                          </p>
                        </div>
                        <span
                          className={`text-[10px] px-2 py-0.5 rounded ${
                            facility.accent
                              ? "bg-secondary-container/10 text-secondary-container"
                              : "bg-error/10 text-error"
                          }`}
                        >
                          {facility.matched}
                        </span>
                      </div>
                      <div className="flex items-center justify-between text-xs text-on-surface-variant mt-3 pt-3 border-t border-white/5">
                        <span>{facility.load}</span>
                        <span className="material-symbols-outlined text-base">
                          arrow_forward_ios
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              {/* Assets */}
              <div className="w-full md:w-1/2 bg-black/20">
                <div className="p-4 bg-white/5 flex items-center justify-between">
                  <span className="text-xs font-bold text-on-surface-variant uppercase tracking-widest">
                    Available Assets (Supply)
                  </span>
                  <span className="bg-surface-container text-[10px] px-2 py-0.5 rounded text-on-surface-variant">
                    REC / PPA
                  </span>
                </div>
                <div className="p-4 space-y-3">
                  {ASSETS.map((asset) => (
                    <div
                      key={asset.id}
                      className="glass-card p-4 rounded-xl border-dashed border-white/20 hover:border-primary/50 cursor-grab transition-all"
                    >
                      <div className="flex gap-3">
                        <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
                          <span className="material-symbols-outlined text-primary-container">
                            {asset.icon}
                          </span>
                        </div>
                        <div className="flex-1">
                          <div className="flex justify-between">
                            <span className="text-[10px] font-bold text-primary uppercase">
                              Asset ID: {asset.id}
                            </span>
                            <span className="text-[10px] text-on-surface-variant">
                              {asset.vintage}
                            </span>
                          </div>
                          <h4 className="text-sm font-medium text-primary mt-1">
                            {asset.name}
                          </h4>
                          <p className="text-xs text-on-surface-variant">
                            {asset.location}
                          </p>
                          <div className="mt-3 flex items-center justify-between">
                            <span className="text-primary-container font-bold">
                              {asset.qty}
                            </span>
                            <span className="material-symbols-outlined text-sm opacity-40">
                              drag_indicator
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </GlassCard>
        </div>
      </div>

      {/* Matched allocation ledger */}
      <GlassCard className="overflow-hidden">
        <div className="p-6 border-b border-white/10 bg-white/[0.02]">
          <h3 className="font-headline-md text-headline-md text-primary">
            Matched Allocation Ledger
          </h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse min-w-[720px]">
            <thead>
              <tr className="text-[10px] font-bold text-on-surface-variant uppercase tracking-widest bg-white/5">
                <th className="px-6 py-4">Transaction ID</th>
                <th className="px-6 py-4">Facility</th>
                <th className="px-6 py-4">Instrument</th>
                <th className="px-6 py-4">Vintage</th>
                <th className="px-6 py-4 text-right">Qty (MWh)</th>
                <th className="px-6 py-4 text-center">Status</th>
              </tr>
            </thead>
            <tbody className="text-sm">
              {LEDGER_ROWS.map((row) => (
                <tr
                  key={row.txId}
                  className="border-b border-white/5 hover:bg-white/[0.02] transition-colors"
                >
                  <td className="px-6 py-4 font-mono text-xs text-primary/70">
                    {row.txId}
                  </td>
                  <td className="px-6 py-4 font-medium">{row.facility}</td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <span className="material-symbols-outlined text-sm text-primary-container">
                        {row.icon}
                      </span>
                      {row.instrument}
                    </div>
                  </td>
                  <td className="px-6 py-4 text-on-surface-variant">
                    {row.vintage}
                  </td>
                  <td className="px-6 py-4 text-right font-bold">
                    {row.qty}
                  </td>
                  <td className="px-6 py-4 text-center">
                    <span
                      className={`px-2 py-1 rounded text-[10px] font-bold border ${
                        row.status === "MATCHED"
                          ? "bg-primary-container/10 text-primary-container border-primary-container/20"
                          : "bg-secondary-container/10 text-secondary-container border-secondary-container/20"
                      }`}
                    >
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
