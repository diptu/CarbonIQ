"use client";

import { useState } from "react";
import { BillingToggle } from "./BillingToggle";

export function PricingTiers() {
  const [isAnnual, setIsAnnual] = useState(false);
  const proPrice = isAnnual ? "$399" : "$499";

  return (
    <>
      <BillingToggle onChange={setIsAnnual} />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-24">
        {/* Community */}
        <div className="glass-card p-8 rounded-xl flex flex-col hover:border-primary/30 transition-all duration-300">
          <div className="mb-8">
            <span className="font-label-sm text-label-sm uppercase tracking-widest text-on-surface-variant mb-2 block">
              Community
            </span>
            <h3 className="font-headline-lg text-headline-lg text-primary mb-4">
              Free
            </h3>
            <p className="text-on-surface-variant text-body-sm font-body-sm">
              Essential tools for independent researchers and climate
              hobbyists.
            </p>
          </div>
          <ul className="space-y-4 mb-8 flex-grow">
            <li className="flex items-center gap-3 text-body-sm font-body-sm">
              <span className="material-symbols-outlined text-primary-container text-lg">
                check_circle
              </span>
              Basic data ingestion
            </li>
            <li className="flex items-center gap-3 text-body-sm font-body-sm">
              <span className="material-symbols-outlined text-primary-container text-lg">
                check_circle
              </span>
              1 project verification
            </li>
            <li className="flex items-center gap-3 text-body-sm font-body-sm">
              <span className="material-symbols-outlined text-primary-container text-lg">
                check_circle
              </span>
              Standard support
            </li>
            <li className="flex items-center gap-3 text-on-surface-variant/50 text-body-sm font-body-sm">
              <span className="material-symbols-outlined text-lg">block</span>
              Advanced AI Estimation
            </li>
          </ul>
          <button className="w-full py-3 rounded-lg border border-white/10 text-primary font-label-md text-label-md hover:bg-white/5 transition-colors">
            Start Free
          </button>
        </div>

        {/* Professional */}
        <div className="glass-card p-8 rounded-xl flex flex-col relative border-primary/40 neon-glow scale-105 z-10">
          <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-primary-container text-on-primary-container text-[10px] font-bold px-4 py-1 rounded-full uppercase tracking-tighter">
            Most Popular
          </div>
          <div className="mb-8">
            <span className="font-label-sm text-label-sm uppercase tracking-widest text-primary-container mb-2 block">
              Professional
            </span>
            <div className="flex items-baseline gap-2">
              <h3 className="font-headline-lg text-headline-lg text-primary">
                {proPrice}
              </h3>
              <span className="text-on-surface-variant text-label-md font-label-md">
                /mo
              </span>
            </div>
            <p className="text-on-surface-variant text-body-sm font-body-sm mt-4">
              For active carbon project developers and institutional
              monitors.
            </p>
          </div>
          <ul className="space-y-4 mb-8 flex-grow">
            {[
              "Advanced AI estimation",
              "10 project verifications",
              "Full API access",
              "Priority support",
            ].map((item) => (
              <li
                key={item}
                className="flex items-center gap-3 text-body-sm font-body-sm"
              >
                <span className="material-symbols-outlined text-primary-container text-lg">
                  verified
                </span>
                {item}
              </li>
            ))}
          </ul>
          <button className="w-full py-3 rounded-lg bg-primary-container text-on-primary-container font-label-md text-label-md hover:opacity-90 transition-all active:scale-95 font-bold">
            Upgrade to Pro
          </button>
        </div>

        {/* Enterprise */}
        <div className="glass-card p-8 rounded-xl flex flex-col hover:border-primary/30 transition-all duration-300">
          <div className="mb-8">
            <span className="font-label-sm text-label-sm uppercase tracking-widest text-on-surface-variant mb-2 block">
              Enterprise
            </span>
            <h3 className="font-headline-lg text-headline-lg text-primary mb-4">
              Custom
            </h3>
            <p className="text-on-surface-variant text-body-sm font-body-sm">
              Bespoke infrastructure for global NGOs and Fortune 500 ESG
              teams.
            </p>
          </div>
          <ul className="space-y-4 mb-8 flex-grow">
            {[
              "Unlimited projects",
              "Dedicated validator nodes",
              "Custom compliance exports",
              "24/7 Premium SLA",
            ].map((item) => (
              <li
                key={item}
                className="flex items-center gap-3 text-body-sm font-body-sm"
              >
                <span className="material-symbols-outlined text-primary-container text-lg">
                  check_circle
                </span>
                {item}
              </li>
            ))}
          </ul>
          <button className="w-full py-3 rounded-lg border border-white/10 text-primary font-label-md text-label-md hover:bg-white/5 transition-colors">
            Contact Sales
          </button>
        </div>
      </div>
    </>
  );
}
