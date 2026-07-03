import type { Metadata } from "next";
import { GlassCard } from "@/components/ui";

export const metadata: Metadata = {
  title: "Marketplace",
  description: "The world's most transparent registry of high-integrity carbon credits.",
};

const CATEGORIES = [
  { icon: "filter_list", label: "All Credits" },
  { icon: "forest", label: "Nature Based", active: true },
  { icon: "water", label: "Blue Carbon" },
  { icon: "bolt", label: "Energy" },
  { icon: "precision_manufacturing", label: "Tech Removal" },
];

const STANDARDS = ["Verra (VCS)", "Gold Standard", "Puro.earth"];

const MARKET_STATS = [
  { label: "Global Composite Index", value: "$24.82", delta: "+4.2%", positive: true },
  { label: "Nature-Based Price", value: "$18.45", delta: "+1.8%", positive: true },
  { label: "Carbon Removal (Tech)", value: "$142.10", delta: "-0.4%", positive: false },
];

const LISTINGS = [
  { icon: "forest", tag: "Nature", title: "Amazonia Reforestation", location: "Brazil, Mato Grosso", vintage: "2023 Vintage", available: "12,450", price: "$22.50", tags: ["Biodiversity", "Water Security", "Verra ID: 1042"] },
  { icon: "bolt", tag: "Energy", title: "Sahara Solar Initiative", location: "Morocco, Ouarzazate", vintage: "2024 Vintage", available: "85,200", price: "$12.10", tags: ["Renewable", "Grid Expansion", "Gold Standard"] },
  { icon: "precision_manufacturing", tag: "Tech Removal", title: "Direct Air Capture II", location: "Iceland, Hellisheiði", vintage: "2024 Vintage", available: "1,200", price: "$480.00", tags: ["Permanent Storage", "High Integrity", "Puro Standard"] },
  { icon: "water", tag: "Blue Carbon", title: "Blue Mangrove Restoration", location: "Indonesia, North Sumatra", vintage: "2022 Vintage", available: "5,300", price: "$34.00", tags: ["Coastal Protection", "High Sequestration", "Verra ID: 3110"] },
];

export default function MarketplacePage() {
  return (
    <div className="flex flex-col lg:flex-row px-6 lg:px-12 py-10 gap-gutter max-w-7xl mx-auto">
      {/* Filter panel */}
      <aside className="w-full lg:w-64 shrink-0 space-y-6">
        <div>
          <h3 className="font-headline-sm text-headline-sm text-primary-fixed-dim mb-1">
            Filters
          </h3>
          <p className="font-body-sm text-body-sm text-on-surface-variant">
            Refine your impact
          </p>
        </div>
        <div>
          <span className="font-label-sm text-label-sm uppercase tracking-wider text-on-surface-variant mb-3 block">
            Categories
          </span>
          <div className="flex flex-col gap-2">
            {CATEGORIES.map((cat) => (
              <button
                key={cat.label}
                className={`flex items-center gap-3 p-2 rounded-lg transition-all ${
                  cat.active
                    ? "bg-secondary-container text-on-secondary-container font-bold"
                    : "text-on-surface-variant hover:bg-surface-variant/40"
                }`}
              >
                <span className="material-symbols-outlined text-body-md">
                  {cat.icon}
                </span>
                <span className="font-label-md text-label-md">
                  {cat.label}
                </span>
              </button>
            ))}
          </div>
        </div>
        <div>
          <span className="font-label-sm text-label-sm uppercase tracking-wider text-on-surface-variant mb-3 block">
            Price Range ($/ton)
          </span>
          <input
            className="w-full h-1 bg-surface-variant rounded-lg appearance-none cursor-pointer accent-primary-container"
            type="range"
          />
          <div className="flex justify-between mt-2 font-label-sm text-label-sm text-on-surface-variant">
            <span>$0</span>
            <span>$500+</span>
          </div>
        </div>
        <div>
          <span className="font-label-sm text-label-sm uppercase tracking-wider text-on-surface-variant mb-3 block">
            Verification Standard
          </span>
          <div className="space-y-2">
            {STANDARDS.map((standard) => (
              <label
                key={standard}
                className="flex items-center gap-2 font-label-md text-label-md cursor-pointer hover:text-on-surface text-on-surface-variant"
              >
                <input
                  className="rounded border-outline-variant bg-transparent text-primary-container focus:ring-primary-container"
                  type="checkbox"
                  defaultChecked={standard === "Verra (VCS)"}
                />
                {standard}
              </label>
            ))}
          </div>
        </div>
        <button className="w-full bg-surface-variant/50 text-on-surface border border-outline-variant/30 py-3 rounded-xl font-label-md text-label-md hover:bg-primary-container hover:text-on-primary-container transition-all">
          Apply Filters
        </button>
      </aside>

      {/* Main content */}
      <main className="flex-1">
        <div className="mb-10">
          <h1 className="font-headline-xl text-headline-xl text-on-surface mb-2">
            CarbonIQ Marketplace
          </h1>
          <p className="font-body-lg text-body-lg text-on-surface-variant max-w-2xl">
            Access the world&apos;s most transparent registry of
            high-integrity carbon credits. Verified by real-time IoT
            monitoring and blockchain provenance.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          {MARKET_STATS.map((stat) => (
            <GlassCard key={stat.label} className="p-6">
              <span className="font-label-sm text-label-sm uppercase tracking-widest text-on-surface-variant">
                {stat.label}
              </span>
              <div className="flex items-end gap-3 mt-2">
                <span className="font-headline-md text-headline-md text-on-surface">
                  {stat.value}
                </span>
                <span
                  className={`text-label-md font-bold mb-1 ${
                    stat.positive ? "text-primary-container" : "text-secondary"
                  }`}
                >
                  {stat.delta}
                </span>
              </div>
            </GlassCard>
          ))}
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-2 gap-gutter">
          {LISTINGS.map((listing) => (
            <GlassCard key={listing.title} className="overflow-hidden group">
              <div className="relative h-48 w-full overflow-hidden bg-gradient-to-br from-primary-container/20 to-surface-container flex items-center justify-center">
                <span className="material-symbols-outlined text-[72px] text-primary-container/30">
                  {listing.icon}
                </span>
                <div className="absolute top-4 left-4 flex gap-2">
                  <span className="bg-primary-container/90 text-on-primary-container px-3 py-1 rounded-full font-label-sm text-label-sm font-bold flex items-center gap-1">
                    <span className="material-symbols-outlined text-[14px]">
                      verified
                    </span>
                    Verified
                  </span>
                  <span className="bg-black/40 backdrop-blur-md text-white px-3 py-1 rounded-full font-label-sm text-label-sm">
                    {listing.tag}
                  </span>
                </div>
              </div>
              <div className="p-6">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="font-headline-md text-headline-md text-on-surface">
                      {listing.title}
                    </h3>
                    <p className="font-body-sm text-body-sm text-on-surface-variant flex items-center gap-1">
                      <span className="material-symbols-outlined text-[16px]">
                        location_on
                      </span>
                      {listing.location}
                    </p>
                  </div>
                  <span className="font-label-sm text-label-sm font-bold text-on-surface-variant bg-surface-variant/50 px-2 py-1 rounded shrink-0">
                    {listing.vintage}
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-4 mb-6">
                  <div className="bg-black/20 p-3 rounded-xl border border-white/5">
                    <span className="font-label-sm text-label-sm text-on-surface-variant block">
                      Available
                    </span>
                    <span className="font-headline-sm text-headline-sm text-on-surface">
                      {listing.available}{" "}
                      <span className="text-body-sm font-normal">tCO2e</span>
                    </span>
                  </div>
                  <div className="bg-black/20 p-3 rounded-xl border border-white/5">
                    <span className="font-label-sm text-label-sm text-on-surface-variant block">
                      Price
                    </span>
                    <span className="font-headline-sm text-headline-sm text-primary-container">
                      {listing.price}{" "}
                      <span className="text-body-sm font-normal text-on-surface">
                        /ton
                      </span>
                    </span>
                  </div>
                </div>
                <div className="flex flex-wrap gap-2 mb-6">
                  {listing.tags.map((tag) => (
                    <span
                      key={tag}
                      className="bg-surface-variant/30 text-on-surface-variant px-2 py-1 rounded font-label-sm text-[10px] uppercase tracking-wider"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
                <div className="flex gap-3">
                  <button className="flex-1 bg-surface-variant/50 text-on-surface py-3 rounded-xl font-label-md text-label-md font-bold hover:bg-surface-variant transition-colors">
                    View Details
                  </button>
                  <button className="flex-1 bg-primary-container text-on-primary-container py-3 rounded-xl font-label-md text-label-md font-bold hover:brightness-110 active:scale-95 transition-all">
                    Add to Registry
                  </button>
                </div>
              </div>
            </GlassCard>
          ))}
        </div>
      </main>
    </div>
  );
}
