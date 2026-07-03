import Link from "next/link";
import { Logo } from "@/components/ui";

const NAV_LINKS = [
  { label: "About", href: "/about" },
  { label: "Methodology", href: "/methodology" },
  { label: "Protocol", href: "/protocol/specifications" },
  { label: "Docs", href: "/docs" },
  { label: "Pricing", href: "/pricing" },
];

export function MarketingHeader({ active }: { active?: string }) {
  return (
    <header className="fixed top-0 left-0 w-full z-50 bg-surface/60 backdrop-blur-lg border-b border-white/10">
      <nav className="container-max flex justify-between items-center px-margin-mobile md:px-margin-desktop h-16">
        <Link
          href="/"
          className="flex items-center gap-2 font-headline-md text-headline-md font-bold text-primary-fixed-dim tracking-tight"
        >
          <Logo size={24} />
          CarbonIQ
        </Link>
        <div className="hidden md:flex gap-8 items-center">
          {NAV_LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={`font-label-md text-label-md transition-colors ${
                active === link.href
                  ? "text-primary-fixed-dim border-b-2 border-primary-fixed-dim pb-1"
                  : "text-on-surface-variant hover:text-primary-fixed-dim"
              }`}
            >
              {link.label}
            </Link>
          ))}
        </div>
        <div className="flex items-center gap-4">
          <Link
            href="/login"
            className="hidden lg:block font-label-md text-label-md text-on-surface hover:opacity-80 transition-opacity"
          >
            Log In
          </Link>
          <Link
            href="/signup"
            className="bg-primary-container text-on-primary-container px-6 py-2.5 rounded-lg font-label-md text-label-md font-bold hover:opacity-90 active:scale-95 transition-all"
          >
            Get Started
          </Link>
        </div>
      </nav>
    </header>
  );
}
