import Logo from "@/components/Logo";

const sections = [
  ["1. What you're agreeing to", "By creating an account, you agree to use Opzy as intended, to discover opportunities you may be eligible for, not to misuse the service or the data of other users."],
  ["2. Who can use this", "Opzy is currently open to invited early-access testers. You're responsible for the accuracy of the profile information you provide, since it's what we use to match you."],
  ["3. About the opportunities we show", "Opzy surfaces opportunities from other organizations. We check what we can, but we don't control application outcomes, eligibility decisions, or whether a listing stays open. Always confirm details with the source before applying."],
  ["4. Your account", "Keep your login details to yourself. You can ask us to delete your account and data at any time during this early-access phase."],
  ["5. Changes", "Since this is an early, actively-changing product, terms may be updated as it develops. We'll let testers know directly if anything meaningfully changes."],
  ["6. Contact", "Questions, reach out directly at iamtjbest15@gmail.com."]
];

export default function Terms() {
  return (
    <div className="min-h-screen w-full bg-white">
      <div className="flex h-20 items-center border-b border-neutral-border px-16">
        <Logo />
      </div>
      <div className="mx-auto max-w-[900px] px-6 py-16">
        <h1 className="text-[32px] font-bold text-primary-navy">Terms & Conditions</h1>
        <p className="mt-3 text-sm text-neutral-slate">
          Last updated: September 2026. This is an early-access product, still being tested with a small group. Terms will be reviewed properly before any public launch.
        </p>
        <div className="mt-8 flex flex-col gap-8">
          {sections.map(([h, b]) => (
            <div key={h}>
              <h2 className="text-lg font-bold text-primary-navy">{h}</h2>
              <p className="mt-1 text-sm text-neutral-slate">{b}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
