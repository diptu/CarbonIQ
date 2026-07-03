import Link from "next/link";

const RESOURCE_LINKS = [
  { label: "Documentation", href: "/docs" },
  { label: "Methodology", href: "/methodology" },
  { label: "Protocol Specs", href: "/protocol/specifications" },
];

const LEGAL_LINKS = [
  { label: "Privacy Policy", href: "#" },
  { label: "Terms of Service", href: "#" },
];

export function MarketingFooter() {
  return (
    <footer className="w-full py-12 px-margin-mobile md:px-margin-desktop bg-surface-container-lowest border-t border-white/5">
      <div className="container-max flex flex-col md:flex-row justify-between gap-gutter">
        <div className="flex flex-col gap-4">
          <span className="font-headline-md text-headline-md font-bold text-primary-fixed-dim">
            CarbonIQ
          </span>
          <p className="font-body-sm text-body-sm text-on-surface-variant max-w-sm">
            © {new Date().getFullYear()} CarbonIQ. Decentralized Environmental
            Integrity.
          </p>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-8">
          <div className="flex flex-col gap-2">
            <span className="font-label-md text-label-md text-primary-fixed-dim uppercase tracking-tighter">
              Resources
            </span>
            {RESOURCE_LINKS.map((link) => (
              <Link
                key={link.label}
                href={link.href}
                className="font-body-sm text-body-sm text-on-surface-variant hover:text-primary-container transition-colors"
              >
                {link.label}
              </Link>
            ))}
          </div>
          <div className="flex flex-col gap-2">
            <span className="font-label-md text-label-md text-primary-fixed-dim uppercase tracking-tighter">
              Legal
            </span>
            {LEGAL_LINKS.map((link) => (
              <Link
                key={link.label}
                href={link.href}
                className="font-body-sm text-body-sm text-on-surface-variant hover:text-primary-container transition-colors"
              >
                {link.label}
              </Link>
            ))}
          </div>
          <div className="flex flex-col gap-2">
            <span className="font-label-md text-label-md text-primary-fixed-dim uppercase tracking-tighter">
              Pricing
            </span>
            <Link
              href="/pricing"
              className="font-body-sm text-body-sm text-on-surface-variant hover:text-primary-container transition-colors"
            >
              Plans &amp; Pricing
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
