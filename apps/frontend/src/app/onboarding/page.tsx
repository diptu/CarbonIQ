import type { Metadata } from "next";
import Link from "next/link";
import { Logo, Input, Select, Textarea, Button } from "@/components/ui";

export const metadata: Metadata = {
  title: "Tenant Onboarding",
  description: "Establish your organization's identity on the CarbonIQ network.",
};

const STEPS = [
  { icon: "domain", label: "Identity", active: true },
  { icon: "lan", label: "Node Deployment" },
  { icon: "group_add", label: "Team Setup" },
  { icon: "fact_check", label: "Review" },
];

const QUICK_STATS = [
  { icon: "bolt", label: "Estimated Uptime", value: "99.98%" },
  { icon: "verified_user", label: "Standard Compliance", value: "ISO 14064" },
  { icon: "database", label: "Storage Tier", value: "Enterprise" },
];

const GUIDANCE = [
  {
    question: "What is a verification node?",
    answer:
      "A dedicated instance that cryptographically signs your climate data before it hits the main chain.",
  },
  {
    question: "How do I invite my auditor?",
    answer:
      "You'll be able to send restricted-access invites in the 'Team Setup' phase to external auditors.",
  },
  {
    question: "Can I change my HQ later?",
    answer:
      "Yes, organization details can be updated via the Tenant Settings menu after onboarding.",
  },
];

export default function OnboardingPage() {
  return (
    <div className="min-h-screen">
      <header className="fixed top-0 w-full z-50 bg-background/80 backdrop-blur-lg border-b border-white/10 flex justify-between items-center px-margin-mobile md:px-margin-desktop h-20">
        <Link href="/" className="flex items-center gap-3">
          <Logo size={32} />
          <span className="font-headline-lg text-headline-lg font-bold text-primary-fixed-dim tracking-tight">
            CarbonIQ
          </span>
        </Link>
        <div className="flex items-center gap-6">
          <span className="material-symbols-outlined text-on-surface-variant hover:text-primary-container transition-colors cursor-pointer">
            help
          </span>
          <div className="flex items-center gap-2 px-4 py-2 bg-surface-container rounded-full border border-white/5">
            <span className="material-symbols-outlined text-primary-fixed-dim">
              account_circle
            </span>
            <span className="font-label-md text-label-md">
              Administrator
            </span>
          </div>
        </div>
      </header>

      <div className="flex pt-20">
        <aside className="hidden lg:flex flex-col fixed left-0 top-20 h-[calc(100vh-80px)] w-72 bg-surface-container-low/60 backdrop-blur-xl border-r border-white/5 py-8 overflow-y-auto">
          <div className="px-8 mb-8">
            <h2 className="font-headline-md text-headline-md text-primary mb-1">
              Tenant Onboarding
            </h2>
            <p className="text-on-surface-variant text-sm">
              Onboarding Progress: 25%
            </p>
            <div className="w-full bg-surface-variant h-1 rounded-full mt-3 overflow-hidden">
              <div className="bg-primary-fixed-dim h-full w-[25%]" />
            </div>
          </div>
          <nav className="flex flex-col flex-grow">
            {STEPS.map((step) => (
              <div
                key={step.label}
                className={`py-4 px-8 flex items-center gap-4 transition-all duration-200 ${
                  step.active
                    ? "bg-primary-container/10 text-primary-fixed-dim border-r-2 border-primary-fixed-dim"
                    : "text-on-surface-variant hover:bg-surface-variant/30 hover:text-primary cursor-pointer"
                }`}
              >
                <span className="material-symbols-outlined">
                  {step.icon}
                </span>
                <span className="font-label-md text-label-md">
                  {step.label}
                </span>
              </div>
            ))}
          </nav>
          <div className="mt-auto px-8 py-6">
            <button className="w-full py-3 bg-surface-container-highest text-on-surface font-label-md text-label-md rounded-lg border border-white/10 hover:bg-surface-bright transition-colors">
              Save Draft
            </button>
          </div>
        </aside>

        <main className="lg:ml-72 flex-grow flex flex-col lg:flex-row p-margin-mobile md:p-margin-desktop gap-gutter">
          <div className="flex-grow max-w-4xl space-y-8">
            <section>
              <h1 className="font-headline-xl text-headline-xl text-primary mb-2">
                Organization Identity
              </h1>
              <p className="font-body-lg text-body-lg text-on-surface-variant max-w-2xl">
                Establish your organization&apos;s digital presence on the
                CarbonIQ network. This information will be used for climate
                ledger transparency and verified reporting.
              </p>
            </section>

            <div className="glass-card p-8 rounded-xl space-y-8">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div className="space-y-6">
                  <Input
                    label="Company Name"
                    placeholder="e.g. Terra Nova Solutions"
                    type="text"
                  />
                  <Input
                    label="HQ Location"
                    placeholder="London, United Kingdom"
                    type="text"
                  />
                  <Select label="Industry Sector">
                    <option>Renewable Energy</option>
                    <option>Supply Chain &amp; Logistics</option>
                    <option>Sustainable Manufacturing</option>
                    <option>Agriculture &amp; Land Use</option>
                  </Select>
                </div>
                <div className="space-y-6">
                  <Textarea
                    label="Sustainability Goals"
                    placeholder="Describe your 2030 Net-Zero roadmap..."
                    rows={3}
                  />
                  <div className="flex flex-col gap-2">
                    <label className="font-label-md text-label-md text-primary-fixed-dim">
                      Organization Logo
                    </label>
                    <div className="border-2 border-dashed border-white/10 rounded-xl p-8 flex flex-col items-center justify-center hover:border-primary-fixed-dim transition-colors cursor-pointer group bg-white/5">
                      <span className="material-symbols-outlined text-4xl text-on-surface-variant group-hover:text-primary-fixed-dim transition-colors mb-2">
                        upload_file
                      </span>
                      <p className="font-label-md text-label-md text-on-surface-variant group-hover:text-primary transition-colors">
                        Click to upload or drag logo
                      </p>
                      <p className="text-[10px] text-on-surface-variant/50 mt-1 uppercase tracking-widest">
                        SVG, PNG or JPG (Max 2MB)
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {QUICK_STATS.map((stat) => (
                <div
                  key={stat.label}
                  className="glass-card p-6 rounded-xl border-l-2 border-primary-fixed-dim"
                >
                  <span className="material-symbols-outlined text-primary-fixed-dim mb-3 block">
                    {stat.icon}
                  </span>
                  <h4 className="font-label-md text-label-md text-primary mb-1">
                    {stat.label}
                  </h4>
                  <p className="font-headline-md text-headline-md text-white">
                    {stat.value}
                  </p>
                </div>
              ))}
            </div>

            <div className="flex justify-between items-center pt-8">
              <button className="px-8 py-3 text-on-surface-variant font-label-md text-label-md hover:text-primary transition-colors flex items-center gap-2">
                <span className="material-symbols-outlined text-sm">
                  arrow_back
                </span>
                Back
              </button>
              <Button size="lg">
                Continue to Node Setup
                <span className="material-symbols-outlined text-sm">
                  arrow_forward
                </span>
              </Button>
            </div>
          </div>

          <aside className="w-full lg:w-80 space-y-6 shrink-0">
            <div className="glass-card p-6 rounded-xl">
              <div className="flex items-center gap-2 mb-4">
                <span className="material-symbols-outlined text-primary-fixed-dim">
                  lightbulb
                </span>
                <h3 className="font-headline-md text-headline-md text-primary text-[18px]">
                  Guidance
                </h3>
              </div>
              <div className="space-y-4">
                {GUIDANCE.map((item, i) => (
                  <div key={item.question}>
                    <h4 className="text-on-surface font-label-md text-label-md mb-2">
                      {item.question}
                    </h4>
                    <p className="text-body-sm text-on-surface-variant/80">
                      {item.answer}
                    </p>
                    {i < GUIDANCE.length - 1 && (
                      <hr className="border-white/5 mt-4" />
                    )}
                  </div>
                ))}
              </div>
              <button className="w-full mt-6 py-2 border border-primary-fixed-dim/30 text-primary-fixed-dim font-label-md text-label-md rounded-lg hover:bg-primary-fixed-dim/10 transition-colors">
                Book a demo call
              </button>
            </div>

            <div className="glass-card p-6 rounded-xl bg-gradient-to-br from-primary-container/5 to-transparent">
              <div className="flex justify-between items-start mb-4">
                <div className="p-2 bg-primary-fixed-dim/20 rounded-lg">
                  <span className="material-symbols-outlined text-primary-fixed-dim">
                    verified
                  </span>
                </div>
                <span className="text-[10px] bg-secondary-container/20 text-secondary-container px-2 py-1 rounded font-bold uppercase tracking-wider">
                  Blockchain Secured
                </span>
              </div>
              <h3 className="font-label-md text-label-md text-white mb-2">
                High Integrity Data
              </h3>
              <p className="text-body-sm text-on-surface-variant">
                CarbonIQ uses decentralized ledgers to ensure your
                environmental claims are immutable and tamper-proof.
              </p>
            </div>
          </aside>
        </main>
      </div>
    </div>
  );
}
