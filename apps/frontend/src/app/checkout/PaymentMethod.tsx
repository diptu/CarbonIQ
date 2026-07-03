"use client";

import { useState } from "react";
import { Input, Button } from "@/components/ui";

export function PaymentMethod() {
  const [method, setMethod] = useState<"crypto" | "fiat">("crypto");

  return (
    <>
      <div className="glass-card p-6 rounded-xl">
        <h2 className="font-headline-md text-headline-md mb-6">
          Payment Method
        </h2>
        <div className="grid grid-cols-2 gap-4">
          <button
            onClick={() => setMethod("crypto")}
            className={`flex flex-col items-center justify-center p-4 rounded-lg border-2 transition-all ${
              method === "crypto"
                ? "border-primary-container bg-primary/5"
                : "border-white/5 bg-white/5 hover:bg-white/10 opacity-60"
            }`}
          >
            <span className="material-symbols-outlined mb-2 text-primary-container">
              account_balance_wallet
            </span>
            <span className="font-label-md text-label-md text-primary">
              Crypto Wallet
            </span>
          </button>
          <button
            onClick={() => setMethod("fiat")}
            className={`flex flex-col items-center justify-center p-4 rounded-lg border-2 transition-all ${
              method === "fiat"
                ? "border-primary-container bg-primary/5"
                : "border-white/5 bg-white/5 hover:bg-white/10 opacity-60"
            }`}
          >
            <span className="material-symbols-outlined mb-2">payments</span>
            <span className="font-label-md text-label-md text-on-surface-variant">
              Fiat / Credit Card
            </span>
          </button>
        </div>
      </div>

      <div className="glass-card p-8 rounded-xl">
        {method === "crypto" ? (
          <div className="text-center py-8">
            <div className="w-16 h-16 bg-primary-container/10 rounded-full flex items-center justify-center mx-auto mb-6">
              <span className="material-symbols-outlined text-primary-container text-4xl">
                sensors
              </span>
            </div>
            <h3 className="font-headline-md text-headline-md mb-2">
              Connect Your Wallet
            </h3>
            <p className="text-on-surface-variant mb-8 px-8">
              Pay securely using Ethereum, Polygon, or CarbonIQ Governance
              tokens.
            </p>
            <div className="space-y-4 max-w-sm mx-auto">
              {["MetaMask", "WalletConnect"].map((wallet) => (
                <button
                  key={wallet}
                  className="w-full flex items-center justify-between p-4 rounded-lg bg-white/5 border border-white/10 hover:border-primary-container/50 transition-all group"
                >
                  <span className="font-label-md">{wallet}</span>
                  <span className="material-symbols-outlined text-on-surface-variant group-hover:translate-x-1 transition-transform">
                    chevron_right
                  </span>
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input label="FULL NAME" placeholder="John Doe" type="text" />
              <Input
                label="EMAIL ADDRESS"
                placeholder="john@example.com"
                type="email"
              />
            </div>
            <Input
              label="CARD DETAILS"
              placeholder="0000 0000 0000 0000"
              type="text"
            />
            <div className="grid grid-cols-2 gap-4">
              <Input label="EXPIRY DATE" placeholder="MM / YY" type="text" />
              <Input label="CVC" placeholder="123" type="text" />
            </div>
            <Button size="lg" className="w-full mt-2">
              Process Payment
            </Button>
          </div>
        )}
      </div>

      <div className="flex flex-wrap items-center justify-center gap-8 py-4">
        {[
          ["verified_user", "SEC AUDITED"],
          ["lock", "SSL ENCRYPTED"],
          ["eco", "CARBON NEUTRAL"],
        ].map(([icon, label]) => (
          <div key={label} className="flex items-center gap-2 opacity-60">
            <span className="material-symbols-outlined text-primary-container">
              {icon}
            </span>
            <span className="font-label-sm text-label-sm">{label}</span>
          </div>
        ))}
      </div>
    </>
  );
}
