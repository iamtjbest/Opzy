import Link from "next/link";

import VerifyEmailCard from "@/components/VerifyEmailCard";
import Logo from "@/components/Logo";

export default async function VerifyEmail({
  searchParams,
}: {
  searchParams: Promise<{ token?: string }>;
}) {
  const { token } = await searchParams;

  return (
    <div className="flex min-h-screen w-full items-center justify-center bg-neutral-mist px-4 py-16">
      <div className="w-full max-w-[440px] rounded-2xl border border-neutral-border bg-white p-8">
        <div className="mb-8 flex flex-col items-center gap-3">
          <Logo size={40} />
          <h1 className="text-2xl font-bold text-primary-navy">Confirm your email</h1>
        </div>

        {token ? (
          <VerifyEmailCard token={token} />
        ) : (
          <div className="flex flex-col items-center gap-3 text-center">
            <p className="text-sm text-neutral-slate">
              This link is missing its confirmation code. Open the link from the email
              exactly as it was sent, or ask for a new one.
            </p>
            <Link href="/login" className="text-[13px] font-bold text-primary-blue">
              Back to log in
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
