"use client";

import { useState } from "react";

export interface SegmentedOption {
  label: string;
  value: string;
}

export function SegmentedControl({
  options,
  defaultValue,
  onChange,
}: {
  options: SegmentedOption[];
  defaultValue?: string;
  onChange?: (value: string) => void;
}) {
  const [active, setActive] = useState(defaultValue ?? options[0]?.value);

  function select(value: string) {
    setActive(value);
    onChange?.(value);
  }

  return (
    <div className="inline-flex items-center gap-1 rounded-full border border-white/10 bg-surface-container-high p-1">
      {options.map((option) => (
        <button
          key={option.value}
          type="button"
          onClick={() => select(option.value)}
          className={`px-4 py-1.5 rounded-full font-label-md text-label-md transition-all ${
            active === option.value
              ? "bg-primary-container text-on-primary-container font-bold"
              : "text-on-surface-variant hover:text-on-surface"
          }`}
        >
          {option.label}
        </button>
      ))}
    </div>
  );
}
