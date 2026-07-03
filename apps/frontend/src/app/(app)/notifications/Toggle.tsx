"use client";

import { useState } from "react";

export function Toggle({ defaultOn = false }: { defaultOn?: boolean }) {
  const [on, setOn] = useState(defaultOn);

  return (
    <button
      onClick={() => setOn(!on)}
      className={`w-10 h-5 rounded-full relative transition-colors ${
        on ? "bg-primary-container" : "bg-surface-variant"
      }`}
    >
      <div
        className={`absolute top-1 w-3 h-3 rounded-full transition-all ${
          on ? "right-1 bg-on-primary-fixed" : "left-1 bg-on-surface-variant"
        }`}
      />
    </button>
  );
}
