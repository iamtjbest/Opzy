import Logo from "@/components/Logo";

const sections = [
  ["1. Acceptance of Terms", "Placeholder. Describe what using Opzy means the person agrees to."],
  ["2. Eligibility", "Placeholder. Minimum age, account requirements, accuracy of profile information."],
  ["3. Use of the Service", "Placeholder. What the service does, acceptable use, prohibited behavior."],
  [
    "4. Opportunity Listings Disclaimer",
    "Placeholder. Opzy surfaces third-party opportunities; it does not guarantee outcomes, eligibility decisions, or that a listing remains open. Verify details directly with the listing source before applying.",
  ],
  ["5. User Accounts", "Placeholder. Account creation, responsibility for credentials, termination conditions."],
  ["6. Limitation of Liability", "Placeholder. Standard liability limitations, reviewed by counsel before publishing."],
  ["7. Changes to These Terms", "Placeholder. How and when terms may be updated, and how users are notified."],
  ["8. Contact", "Placeholder. Support/legal contact details."],
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
          Last updated: [date]. Replace placeholder sections below with reviewed legal copy
          before publishing.
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
