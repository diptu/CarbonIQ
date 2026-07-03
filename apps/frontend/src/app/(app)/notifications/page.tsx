import type { Metadata } from "next";
import { GlassCard } from "@/components/ui";
import { Toggle } from "./Toggle";

export const metadata: Metadata = {
  title: "Notifications & Alerts",
  description: "Stay on top of reports, AI insights, and compliance events.",
};

const NOTIFICATIONS = [
  {
    icon: "description",
    iconColor: "text-primary-container",
    iconBg: "bg-primary-container/10 border-primary-container/20",
    title: "Q3 Sustainability Ledger Generated",
    time: "2m ago",
    detail:
      "Verification complete. The quarterly ledger for European operations has been anchored to the blockchain.",
    cta: "View Report",
    ctaClass: "bg-primary-container text-on-primary-fixed",
    tag: "Reporting",
    tagClass: "border-primary-container/30 text-primary-container",
  },
  {
    icon: "psychology",
    iconColor: "text-secondary",
    iconBg: "bg-secondary/10 border-secondary/20",
    title: "Load Profile Accuracy hit 98% for Tesla Giga Berlin",
    time: "1h ago",
    detail:
      "The AI Engine has successfully refined the prediction model for high-density industrial hubs.",
    cta: "Analyze Data",
    ctaClass: "border border-white/20 text-on-surface hover:bg-white/5",
    tag: "AI Engine",
    tagClass: "border-secondary/30 text-secondary",
    accent: "border-l-secondary",
  },
  {
    icon: "warning",
    iconColor: "text-tertiary-fixed",
    iconBg: "bg-tertiary-fixed/10 border-tertiary-fixed/20",
    title: "Action Required: Data Gap in NSW Data Center",
    time: "3h ago",
    detail:
      "Ingestion failed for the smart meter array at the Sydney Southwest facility. Compliance threshold at risk.",
    cta: "Fix Gap",
    ctaClass: "bg-tertiary-fixed text-on-tertiary-fixed",
    tag: "Ingestion",
    tagClass: "border-tertiary-fixed/30 text-tertiary-fixed",
    accent: "border-l-tertiary-fixed",
  },
  {
    icon: "person_add",
    iconColor: "text-on-surface",
    iconBg: "bg-white/5 border-white/10",
    title: "New Tenant 'EcoGrid' onboarded successfully",
    time: "6h ago",
    detail:
      "Governance protocols initialized. API keys issued to the EcoGrid administrator team.",
    cta: "Manage Access",
    ctaClass: "border border-white/20 text-on-surface hover:bg-white/5",
    tag: "IAM",
    tagClass: "border-white/10 text-on-surface-variant",
  },
];

const TABS = ["All Notifications", "Reports", "AI Insights", "Compliance"];

const SYSTEM_STATUS = [
  { label: "Ingestion Hub", status: "Operational", value: 99, color: "bg-primary-container", statusColor: "text-primary-container" },
  { label: "AI Engine", status: "Peak Performance", value: 94, color: "bg-primary-container", statusColor: "text-primary-container" },
  { label: "Blockchain Ledger", status: "Synchronized", value: 100, color: "bg-secondary", statusColor: "text-secondary" },
];

export default function NotificationsPage() {
  return (
    <div className="max-w-7xl mx-auto px-6 lg:px-12 py-12 flex flex-col md:flex-row gap-gutter">
      {/* Feed */}
      <section className="flex-1 space-y-8">
        <div className="flex flex-col gap-2">
          <h1 className="font-headline-xl text-headline-xl text-primary-fixed">
            Notifications &amp; Alerts
          </h1>
          <p className="font-body-lg text-body-lg text-on-surface-variant">
            You have{" "}
            <span className="text-primary-container font-bold">
              3 unread
            </span>{" "}
            critical updates from the last 24 hours.
          </p>
        </div>

        <div className="flex gap-8 border-b border-white/5">
          {TABS.map((tab, i) => (
            <button
              key={tab}
              className={`font-label-md text-label-md py-4 relative ${
                i === 0
                  ? "text-primary-fixed"
                  : "text-on-surface-variant hover:text-primary-fixed transition-colors"
              }`}
            >
              {tab}
              {i === 0 && (
                <div className="absolute bottom-[-1px] left-0 right-0 h-0.5 bg-primary-fixed" />
              )}
            </button>
          ))}
        </div>

        <div className="space-y-4">
          {NOTIFICATIONS.map((item) => (
            <GlassCard
              key={item.title}
              className={`p-6 flex gap-5 ${item.accent ? `border-l-4 ${item.accent}` : ""}`}
            >
              <div
                className={`w-12 h-12 rounded-lg flex items-center justify-center border shrink-0 ${item.iconBg}`}
              >
                <span
                  className={`material-symbols-outlined ${item.iconColor}`}
                >
                  {item.icon}
                </span>
              </div>
              <div className="flex-1">
                <div className="flex justify-between items-start mb-1 gap-4">
                  <h3 className="font-headline-md text-body-md font-semibold text-on-surface">
                    {item.title}
                  </h3>
                  <span className="font-label-sm text-label-sm text-on-surface-variant shrink-0">
                    {item.time}
                  </span>
                </div>
                <p className="text-on-surface-variant text-body-sm mb-4">
                  {item.detail}
                </p>
                <div className="flex items-center gap-3">
                  <button
                    className={`px-4 py-1.5 rounded-lg font-label-md text-label-sm transition-all ${item.ctaClass}`}
                  >
                    {item.cta}
                  </button>
                  <span
                    className={`text-[10px] px-2 py-0.5 rounded border uppercase tracking-widest font-bold ${item.tagClass}`}
                  >
                    {item.tag}
                  </span>
                </div>
              </div>
            </GlassCard>
          ))}
        </div>
      </section>

      {/* Widgets */}
      <aside className="w-full md:w-80 space-y-gutter shrink-0">
        <GlassCard className="p-6">
          <h2 className="font-headline-md text-body-md font-bold mb-4 text-on-surface flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-primary-container animate-pulse" />
            System Status
          </h2>
          <div className="space-y-4">
            {SYSTEM_STATUS.map((item) => (
              <div key={item.label}>
                <div className="flex justify-between items-center mb-1">
                  <span className="text-body-sm text-on-surface-variant">
                    {item.label}
                  </span>
                  <span
                    className={`font-label-sm text-label-sm ${item.statusColor}`}
                  >
                    {item.status}
                  </span>
                </div>
                <div className="w-full h-1 bg-white/5 rounded-full overflow-hidden">
                  <div
                    className={`h-full ${item.color}`}
                    style={{ width: `${item.value}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </GlassCard>

        <GlassCard className="p-6">
          <h2 className="font-headline-md text-body-md font-bold mb-4 text-on-surface">
            Alert Preferences
          </h2>
          <div className="space-y-6">
            <div>
              <p className="font-label-md text-label-sm text-primary-fixed uppercase tracking-wider mb-3">
                Reporting &amp; Compliance
              </p>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-body-sm text-on-surface-variant">
                    Web Notifications
                  </span>
                  <Toggle defaultOn />
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-body-sm text-on-surface-variant">
                    Email Summaries
                  </span>
                  <Toggle />
                </div>
              </div>
            </div>
            <div>
              <p className="font-label-md text-label-sm text-primary-fixed uppercase tracking-wider mb-3">
                System &amp; Security
              </p>
              <div className="flex items-center justify-between">
                <span className="text-body-sm text-on-surface-variant">
                  Critical Push Alerts
                </span>
                <Toggle defaultOn />
              </div>
            </div>
          </div>
          <button className="w-full mt-6 py-2 rounded-lg border border-white/10 hover:border-primary-fixed/30 hover:text-primary-fixed transition-all font-label-md text-label-sm">
            Manage All Settings
          </button>
        </GlassCard>
      </aside>
    </div>
  );
}
