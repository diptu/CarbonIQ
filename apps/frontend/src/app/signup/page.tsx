import type { Metadata } from "next";
import Link from "next/link";
import { Logo } from "@/components/ui";
import { AuthCard } from "@/components/marketing/AuthCard";

export const metadata: Metadata = {
  title: "Secure Access",
  description: "Create your CarbonIQ account.",
};

export default function SignupPage() {
  return (
    <>
      <header className="fixed top-0 left-0 right-0 z-50">
        <nav className="flex justify-between items-center w-full px-margin-mobile md:px-margin-desktop py-6 container-max mx-auto">
          <Link href="/" className="flex items-center gap-3">
            <Logo size={28} />
            <span className="font-headline-md text-headline-md font-bold text-primary">
              CarbonIQ
            </span>
          </Link>
          <div className="flex items-center gap-6">
            <Link
              href="/"
              className="hidden md:block text-on-surface-variant hover:text-primary transition-colors font-label-md text-label-md"
            >
              Platform
            </Link>
            <Link
              href="/docs"
              className="hidden md:block text-on-surface-variant hover:text-primary transition-colors font-label-md text-label-md"
            >
              Research
            </Link>
          </div>
        </nav>
      </header>

      <main className="relative flex-grow flex items-center justify-center pt-24 pb-12 px-margin-mobile grid-bg">
        <AuthCard defaultTab="signup" />
      </main>

      <footer className="mt-auto">
        <div className="flex flex-col md:flex-row justify-between items-center w-full px-margin-mobile md:px-margin-desktop py-8 container-max mx-auto gap-4">
          <span className="font-label-md text-label-md text-on-surface-variant">
            © {new Date().getFullYear()} CarbonIQ. Verified Environmental
            Intelligence.
          </span>
          <div className="flex items-center gap-2">
            <div className="w-1.5 h-1.5 bg-primary-container rounded-full animate-pulse" />
            <span className="font-body-sm text-body-sm text-on-surface-variant">
              Status
            </span>
          </div>
        </div>
      </footer>
    </>
  );
}
