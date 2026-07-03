"use client";

import { useState } from "react";

export function BillingToggle({
  onChange,
}: {
  onChange: (annual: boolean) => void;
}) {
  const [isAnnual, setIsAnnual] = useState(false);

  function toggle() {
    const next = !isAnnual;
    setIsAnnual(next);
    onChange(next);
  }

  return (
    <div className="flex items-center justify-center gap-4 mb-8">
      <span
        className={`font-label-md text-label-md text-on-surface-variant ${
          isAnnual ? "opacity-50" : ""
        }`}
      >
        Monthly
      </span>
      <button
        onClick={toggle}
        className={`relative w-14 h-7 rounded-full p-1 transition-colors duration-300 ${
          isAnnual ? "bg-primary-container/20" : "bg-surface-container-high"
        }`}
      >
        <div
          className="w-5 h-5 bg-primary-container rounded-full shadow-lg transform transition-transform duration-300"
          style={{ transform: isAnnual ? "translateX(28px)" : "translateX(0)" }}
        />
      </button>
      <span
        className={`font-label-md text-label-md flex items-center gap-2 ${
          isAnnual ? "text-primary" : "text-on-surface-variant"
        }`}
      >
        Annual{" "}
        <span className="bg-primary/10 text-primary-container px-2 py-0.5 rounded text-[10px] uppercase font-bold border border-primary/20">
          Save 20%
        </span>
      </span>
    </div>
  );
}
