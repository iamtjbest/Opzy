import Logo from "@/components/Logo";
import Link from "next/link";

export default function AboutPage() {
  return (
    <div className="flex w-full flex-col min-h-screen bg-white">
      {/* Nav */}
      <div className="fixed top-0 left-1/2 z-10 flex h-20 w-full max-w-[1440px] -translate-x-1/2 items-center justify-between bg-neutral-mist/65 px-6 lg:px-16 backdrop-blur-sm">
        <Logo />
        <div className="flex items-center gap-6">
          <Link href="/about" className="hidden md:block text-sm font-bold text-primary-navy">
            About
          </Link>
          <Link href="/pricing" className="hidden md:block text-sm font-bold text-neutral-slate hover:text-primary-navy">
            Pricing
          </Link>
          <Link href="/login" className="text-sm font-bold text-primary-navy hover:text-primary-blue">
            Log in
          </Link>
        </div>
      </div>

      <main className="flex-1 flex flex-col items-center justify-center px-6 pt-32 pb-16">
        <div className="max-w-2xl text-center">
          <h1 className="text-4xl font-extrabold text-primary-navy mb-6">About Opzy</h1>
          <div className="text-lg text-neutral-ink leading-relaxed space-y-4">
            <p>
              Opzy started from a simple frustration: opportunities that were worth applying for kept getting missed, not because they didn't exist, but because they were scattered across WhatsApp groups, job boards, and pages nobody has time to check every day.
            </p>
            <p>
              We talked to dozens of students and early-career professionals before writing a line of code, and the same three problems kept coming up: not knowing if you actually qualify, finding things too late, and not knowing what to trust. Opzy is built around those three problems specifically, not around being another place to browse listings.
            </p>
            <p>
              We're early. This is a small, invite-first version, built to get real feedback before it's anything more.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
