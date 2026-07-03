import type { Metadata } from "next";
import { MarketingHeader } from "@/components/marketing/MarketingHeader";
import { MarketingFooter } from "@/components/marketing/MarketingFooter";
import { PaymentMethod } from "./PaymentMethod";

export const metadata: Metadata = {
  title: "Secure Checkout",
  description: "Complete your CarbonIQ subscription.",
};

export default function CheckoutPage() {
  return (
    <>
      <MarketingHeader />
      <main className="pt-24 pb-16 px-margin-mobile md:px-margin-desktop container-max">
        <header className="mb-12 text-center">
          <h1 className="font-headline-xl text-headline-xl mb-4">
            Complete Your Subscription
          </h1>
          <p className="text-on-surface-variant max-w-xl mx-auto">
            Secure your institutional-grade climate data stream and start
            offsetting your footprint with blockchain transparency.
          </p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-gutter">
          <div className="lg:col-span-7 space-y-gutter">
            <PaymentMethod />
          </div>

          <div className="lg:col-span-5">
            <div className="glass-card rounded-xl sticky top-24 overflow-hidden">
              <div className="p-8 border-b border-white/10">
                <h2 className="font-headline-md text-headline-md mb-6">
                  Order Summary
                </h2>
                <div className="flex items-start justify-between mb-8">
                  <div>
                    <div className="inline-flex items-center gap-2 px-2 py-1 bg-primary-container/10 rounded mb-2">
                      <span className="w-2 h-2 rounded-full bg-primary-container verified-badge-glow" />
                      <span className="font-label-sm text-label-sm text-primary-container uppercase tracking-widest">
                        Enterprise Tier
                      </span>
                    </div>
                    <p className="font-body-md text-on-surface">
                      Institutional Data Access
                    </p>
                    <p className="font-label-sm text-label-sm text-on-surface-variant">
                      Billed Annually
                    </p>
                  </div>
                  <p className="font-headline-md text-headline-md text-primary">
                    $2,400
                  </p>
                </div>
                <div className="space-y-4">
                  <div className="flex justify-between font-label-md text-label-md text-on-surface-variant">
                    <span>Subtotal</span>
                    <span>$2,400.00</span>
                  </div>
                  <div className="flex justify-between font-label-md text-label-md text-on-surface-variant">
                    <span>Platform Fee (0%)</span>
                    <span className="text-primary-container">FREE</span>
                  </div>
                  <div className="flex justify-between font-label-md text-label-md text-on-surface-variant">
                    <span>On-chain Verification</span>
                    <span>$0.45</span>
                  </div>
                </div>
              </div>
              <div className="p-8 bg-white/5">
                <div className="flex justify-between items-center mb-6">
                  <span className="font-headline-md text-headline-md">
                    Total Due
                  </span>
                  <span className="font-headline-lg text-headline-lg text-primary">
                    $2,400.45
                  </span>
                </div>
                <div className="flex items-start gap-3 p-4 rounded-lg bg-surface-container-high border border-white/5">
                  <span className="material-symbols-outlined text-primary-container">
                    info
                  </span>
                  <p className="font-body-sm text-body-sm text-on-surface-variant leading-relaxed">
                    You are saving{" "}
                    <span className="text-primary">$400/year</span> by
                    choosing the annual billing cycle. Verified environmental
                    credits will be issued to your wallet upon confirmation.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
      <MarketingFooter />
    </>
  );
}
