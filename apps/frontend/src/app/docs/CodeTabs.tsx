"use client";

import { useState } from "react";

const SNIPPETS: Record<string, string> = {
  js: `const ciq = require('@carboniq/sdk');

const client = new ciq.Client({
  apiKey: 'your_api_key_here',
  environment: 'mainnet'
});

// Query environmental metrics for a specific block
const metrics = await client.getEnvironmentalMetrics({
  assetId: 'AMZN-RE-2024',
  range: '30d'
});

console.log(metrics);`,
  py: `import carboniq

client = carboniq.Client(
    api_key="your_api_key_here",
    environment="mainnet"
)

# Fetch recent verified offsets
offsets = client.get_verified_offsets(limit=5)
for offset in offsets:
    print(offset.total_co2_sequestered)`,
  sol: `pragma solidity ^0.8.20;

import "@carboniq/contracts/ICarbonIQOracle.sol";

contract CarbonCheck {
    ICarbonIQOracle public oracle;

    constructor(address _oracle) {
        oracle = ICarbonIQOracle(_oracle);
    }

    function isProjectVerified(bytes32 projectId) external view returns (bool) {
        return oracle.isVerified(projectId);
    }
}`,
};

const TABS = [
  { key: "js", label: "JavaScript" },
  { key: "py", label: "Python" },
  { key: "sol", label: "Solidity" },
];

export function CodeTabs() {
  const [active, setActive] = useState("js");

  return (
    <div className="glass-card rounded-xl overflow-hidden mb-8">
      <div className="flex items-center justify-between px-6 py-3 bg-surface-container-high/50 border-b border-white/10">
        <div className="flex gap-6">
          {TABS.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActive(tab.key)}
              className={`font-label-sm text-label-sm transition-colors ${
                active === tab.key
                  ? "text-primary border-b-2 border-primary"
                  : "text-on-surface-variant hover:text-on-surface"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
        <button className="text-on-surface-variant hover:text-primary transition-colors">
          <span className="material-symbols-outlined text-sm">
            content_copy
          </span>
        </button>
      </div>
      <div className="p-6 font-mono text-body-sm leading-relaxed overflow-x-auto">
        <pre className="text-on-surface-variant whitespace-pre-wrap">
          {SNIPPETS[active]}
        </pre>
      </div>
    </div>
  );
}
