import Logo from "@/components/Logo";
import Link from "next/link";
import Button from "@/components/Button";

export default function PricingPage() {
  return (
    <div className="flex w-full flex-col min-h-screen bg-white">
      {/* Nav */}
      <div className="fixed top-0 left-1/2 z-10 flex h-20 w-full max-w-[1440px] -translate-x-1/2 items-center justify-between bg-neutral-mist/65 px-6 lg:px-16 backdrop-blur-sm">
        <Logo />
        <div className="flex items-center gap-6">
          <Link href="/about" className="hidden md:block text-sm font-bold text-neutral-slate hover:text-primary-navy">
            About
          </Link>
          <Link href="/pricing" className="hidden md:block text-sm font-bold text-primary-navy">
            Pricing
          </Link>
          <Link href="/login" className="text-sm font-bold text-primary-navy hover:text-primary-blue">
            Log in
          </Link>
        </div>
      </div>

      <main className="flex-1 flex flex-col items-center justify-center px-6 pt-32 pb-16">
        <div className="max-w-4xl text-center">
          <h1 className="text-4xl font-extrabold text-primary-navy mb-4">Simple Pricing</h1>
          <p className="text-lg text-neutral-ink mb-12">Start for free, upgrade when you need more power.</p>
          
          <div className="grid md:grid-cols-2 gap-8 max-w-3xl mx-auto text-left">
            <div className="border border-neutral-border rounded-2xl p-8 bg-neutral-mist">
              <h2 className="text-2xl font-bold text-primary-navy mb-2">Free</h2>
              <p className="text-neutral-slate mb-6">Core matching experience.</p>
              <div className="text-4xl font-extrabold text-primary-navy mb-8">$0</div>
              <ul className="flex flex-col gap-3 mb-8 text-neutral-ink">
                <li className="flex items-center gap-2">✓ Basic matching</li>
                <li className="flex items-center gap-2">✓ Daily digests</li>
                <li className="flex items-center gap-2">✓ Standard support</li>
              </ul>
              <Button className="w-full justify-center" href="/">Get Started</Button>
            </div>
            
            <div className="border-2 border-primary-blue rounded-2xl p-8 bg-white relative">
              <div className="absolute top-0 right-8 -translate-y-1/2 bg-primary-blue text-white text-xs font-bold px-3 py-1 rounded-full">
                COMING SOON
              </div>
              <h2 className="text-2xl font-bold text-primary-navy mb-2">Pro</h2>
              <p className="text-neutral-slate mb-6">For power seekers.</p>
              <div className="text-4xl font-extrabold text-primary-navy mb-8">TBD</div>
              <ul className="flex flex-col gap-3 mb-8 text-neutral-ink">
                <li className="flex items-center gap-2">✓ Deep personalization</li>
                <li className="flex items-center gap-2">✓ Unlimited tracking</li>
                <li className="flex items-center gap-2">✓ Real-time alerts</li>
              </ul>
              <Button variant="outline-dark" className="w-full justify-center" href="/">Join Waitlist</Button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
