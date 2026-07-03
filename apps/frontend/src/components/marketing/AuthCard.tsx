"use client";

import { useState } from "react";
import Link from "next/link";
import { Logo, Input, Button } from "@/components/ui";

const SSO_PROVIDERS = ["Azure AD", "Google", "Okta"];

export function AuthCard({ defaultTab }: { defaultTab: "signin" | "signup" }) {
  const [tab, setTab] = useState<"signin" | "signup">(defaultTab);

  return (
    <div className="relative z-10 w-full max-w-md">
      <div className="glass-card rounded-xl p-8 shadow-2xl">
        <div className="flex flex-col items-center mb-8">
          <div className="w-16 h-16 mb-4 flex items-center justify-center relative">
            <Logo size={48} />
          </div>
          <h1 className="font-headline-lg text-headline-lg text-primary text-center">
            Verified Access
          </h1>
          <p className="font-body-sm text-body-sm text-on-surface-variant text-center mt-2">
            Connecting to environmental intelligence
          </p>
        </div>

        <div className="flex border-b border-outline-variant/30 mb-8">
          <button
            onClick={() => setTab("signin")}
            className={`flex-1 pb-2 font-label-md text-label-md transition-all ${
              tab === "signin"
                ? "text-primary border-b-2 border-primary-container -mb-px"
                : "text-on-surface-variant"
            }`}
          >
            Sign In
          </button>
          <button
            onClick={() => setTab("signup")}
            className={`flex-1 pb-2 font-label-md text-label-md transition-all ${
              tab === "signup"
                ? "text-primary border-b-2 border-primary-container -mb-px"
                : "text-on-surface-variant"
            }`}
          >
            Sign Up
          </button>
        </div>

        <form
          className="space-y-6"
          onSubmit={(e) => e.preventDefault()}
        >
          <div className="space-y-4">
            {tab === "signup" && (
              <Input label="Full Name" placeholder="Jane Smith" type="text" />
            )}
            <Input
              label="Email Address"
              placeholder="name@company.com"
              type="email"
            />
            <div>
              <div className="flex justify-between items-center mb-1">
                <label className="font-label-sm text-label-sm text-on-surface-variant">
                  Password
                </label>
                {tab === "signin" && (
                  <Link
                    href="#"
                    className="text-primary-fixed-dim hover:text-primary-container font-label-sm text-label-sm transition-colors"
                  >
                    Forgot?
                  </Link>
                )}
              </div>
              <Input placeholder="••••••••" type="password" />
            </div>
          </div>
          <Button type="submit" className="w-full" size="lg">
            {tab === "signin" ? "Continue to Terminal" : "Initialize Account"}
            <span className="material-symbols-outlined text-sm">
              arrow_forward
            </span>
          </Button>
        </form>

        <div className="mt-8">
          <div className="flex items-center gap-4 mb-6">
            <div className="h-px bg-outline-variant/30 flex-grow" />
            <span className="font-label-sm text-label-sm text-on-surface-variant shrink-0">
              Or continue with
            </span>
            <div className="h-px bg-outline-variant/30 flex-grow" />
          </div>
          <div className="grid grid-cols-3 gap-3">
            {SSO_PROVIDERS.map((provider) => (
              <button
                key={provider}
                type="button"
                className="flex items-center justify-center py-2.5 px-4 bg-white/5 border border-white/10 rounded-lg hover:bg-white/10 transition-colors text-label-sm text-on-surface-variant"
                aria-label={provider}
              >
                {provider}
              </button>
            ))}
          </div>
        </div>

        <div className="mt-8 flex justify-center">
          <div className="flex items-center gap-2 px-3 py-1.5 bg-primary-container/5 border border-primary-container/20 rounded-full">
            <span
              className="material-symbols-outlined text-primary-container"
              style={{ fontVariationSettings: "'FILL' 1", fontSize: 14 }}
            >
              verified_user
            </span>
            <span className="font-label-sm text-[10px] uppercase tracking-widest text-primary-container/80">
              Secured by Verified Protocol v2.1
            </span>
          </div>
        </div>
      </div>
      <p className="text-center mt-6 font-body-sm text-body-sm text-on-surface-variant/60">
        Authorized access only. All sessions are monitored for environmental
        compliance and ledger integrity.
      </p>
    </div>
  );
}
