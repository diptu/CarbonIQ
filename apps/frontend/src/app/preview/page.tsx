import type { Metadata } from "next";
import {
  Button,
  GlassCard,
  StatusBadge,
  Input,
  Textarea,
  Select,
  SegmentedControl,
  MetricCircle,
  Logo,
} from "@/components/ui";

export const metadata: Metadata = {
  title: "Component Preview",
  description: "Visual QA gallery for every CarbonIQ UI primitive.",
};

const COLOR_SWATCHES: { name: string; className: string }[] = [
  { name: "background", className: "bg-background" },
  { name: "surface-container", className: "bg-surface-container" },
  { name: "surface-container-high", className: "bg-surface-container-high" },
  { name: "primary-container", className: "bg-primary-container" },
  { name: "secondary-container", className: "bg-secondary-container" },
  { name: "tertiary-container", className: "bg-tertiary-container" },
  { name: "error-container", className: "bg-error-container" },
  { name: "outline-variant", className: "bg-outline-variant" },
];

const TYPE_SCALE: { name: string; font: string; text: string }[] = [
  { name: "headline-xl", font: "font-headline-xl", text: "text-headline-xl" },
  { name: "headline-lg", font: "font-headline-lg", text: "text-headline-lg" },
  { name: "headline-md", font: "font-headline-md", text: "text-headline-md" },
  { name: "body-lg", font: "font-body-lg", text: "text-body-lg" },
  { name: "body-md", font: "font-body-md", text: "text-body-md" },
  { name: "label-md", font: "font-label-md", text: "text-label-md" },
];

function Section({
  title,
  description,
  children,
}: {
  title: string;
  description?: string;
  children: React.ReactNode;
}) {
  return (
    <section className="mb-20">
      <div className="flex items-baseline gap-4 mb-8">
        <h2 className="font-headline-lg text-headline-lg text-on-surface">
          {title}
        </h2>
        <div className="h-px flex-1 bg-white/10" />
      </div>
      {description && (
        <p className="font-body-md text-body-md text-on-surface-variant mb-8 max-w-2xl">
          {description}
        </p>
      )}
      {children}
    </section>
  );
}

export default function ComponentPreviewPage() {
  return (
    <main className="min-h-screen px-margin-mobile md:px-margin-desktop py-16 container-max">
      <header className="mb-16">
        <div className="flex items-center gap-3 mb-4">
          <Logo size={32} />
          <span className="font-label-md text-label-md text-primary-container uppercase tracking-widest">
            Internal / Not linked in nav
          </span>
        </div>
        <h1 className="font-headline-xl text-headline-xl text-primary mb-4">
          Component Preview
        </h1>
        <p className="font-body-lg text-body-lg text-on-surface-variant max-w-2xl">
          Visual QA gallery for every primitive in{" "}
          <code className="bg-white/10 px-1.5 py-0.5 rounded font-mono text-sm text-primary">
            src/components/ui
          </code>
          . Check this page after touching{" "}
          <code className="bg-white/10 px-1.5 py-0.5 rounded font-mono text-sm text-primary">
            globals.css
          </code>{" "}
          or any shared component.
        </p>
      </header>

      <Section title="Color tokens" description="EcoLens / CarbonIQ palette from DESIGN.md.">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-gutter">
          {COLOR_SWATCHES.map((swatch) => (
            <div key={swatch.name} className="glass-card rounded-xl overflow-hidden">
              <div className={`h-20 ${swatch.className}`} />
              <div className="p-3 font-label-sm text-label-sm text-on-surface-variant">
                {swatch.name}
              </div>
            </div>
          ))}
        </div>
      </Section>

      <Section title="Typography">
        <div className="space-y-6">
          {TYPE_SCALE.map((scale) => (
            <div
              key={scale.name}
              className="flex flex-col md:flex-row md:items-baseline gap-2 md:gap-6 border-b border-white/5 pb-6"
            >
              <span className="w-32 shrink-0 font-label-sm text-label-sm text-on-surface-variant">
                {scale.name}
              </span>
              <span className={`${scale.font} ${scale.text} text-on-surface`}>
                The quick brown fox
              </span>
            </div>
          ))}
        </div>
      </Section>

      <Section title="Buttons">
        <div className="flex flex-wrap gap-4 items-center">
          <Button variant="primary">Primary</Button>
          <Button variant="secondary">Secondary</Button>
          <Button variant="outline">Outline</Button>
          <Button variant="ghost">Ghost</Button>
          <Button
            variant="primary"
            icon={<span className="material-symbols-outlined text-[18px]">arrow_forward</span>}
          >
            With icon
          </Button>
          <Button variant="primary" size="lg">
            Large
          </Button>
          <Button variant="primary" disabled>
            Disabled
          </Button>
        </div>
      </Section>

      <Section title="Glass cards">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-gutter">
          <GlassCard className="p-8">
            <h3 className="font-headline-md text-headline-md mb-2">Standard card</h3>
            <p className="font-body-sm text-body-sm text-on-surface-variant">
              Default glass-card recipe: 60% forest-black fill, 16px blur, 10% white border.
            </p>
          </GlassCard>
          <GlassCard className="p-8 neon-glow border-primary-container/40">
            <h3 className="font-headline-md text-headline-md mb-2 text-primary-container">
              Active glow
            </h3>
            <p className="font-body-sm text-body-sm text-on-surface-variant">
              Add <code className="text-primary-container">neon-glow</code> for the elevated / active state.
            </p>
          </GlassCard>
          <GlassCard className="p-8 flex flex-col items-center justify-center">
            <MetricCircle percent={96} />
            <p className="mt-4 font-label-sm text-label-sm text-on-surface-variant">
              Node Efficiency
            </p>
          </GlassCard>
        </div>
      </Section>

      <Section title="Status badges">
        <div className="flex flex-wrap gap-6">
          <StatusBadge variant="pending">Pending</StatusBadge>
          <StatusBadge variant="verified">Verified</StatusBadge>
          <StatusBadge variant="minted">Minted</StatusBadge>
          <StatusBadge variant="flagged">Flagged</StatusBadge>
        </div>
      </Section>

      <Section title="Form fields">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-3xl">
          <Input label="Text input" placeholder="name@company.com" type="email" />
          <Select label="Select">
            <option>Renewable Energy</option>
            <option>Supply Chain &amp; Logistics</option>
          </Select>
          <Textarea
            label="Textarea"
            placeholder="Describe your 2030 Net-Zero roadmap..."
            rows={3}
            className="md:col-span-2"
          />
        </div>
      </Section>

      <Section title="Segmented control">
        <SegmentedControl
          options={[
            { label: "Monthly", value: "monthly" },
            { label: "Annual", value: "annual" },
          ]}
        />
      </Section>

      <Section title="Icons" description="Material Symbols Outlined, used via the .material-symbols-outlined utility class.">
        <div className="flex flex-wrap gap-6">
          {[
            "eco",
            "verified",
            "hub",
            "psychology",
            "security",
            "sensors",
            "satellite_alt",
            "auto_awesome",
          ].map((icon) => (
            <div
              key={icon}
              className="glass-card rounded-xl p-4 flex flex-col items-center gap-2 w-24"
            >
              <span className="material-symbols-outlined text-primary-container text-2xl">
                {icon}
              </span>
              <span className="text-[10px] text-on-surface-variant text-center">
                {icon}
              </span>
            </div>
          ))}
        </div>
      </Section>
    </main>
  );
}
