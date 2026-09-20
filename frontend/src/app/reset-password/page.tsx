import Link from "next/link";

import ResetPasswordForm from "@/components/ResetPasswordForm";

export default async function ResetPassword({
  searchParams,
}: {
  searchParams: Promise<{ token?: string }>;
}) {
  const { token } = await searchParams;

  return (
    <div className="flex min-h-screen w-full items-center justify-center bg-neutral-mist px-4 py-16">
      <div className="w-full max-w-[440px] rounded-2xl border border-neutral-border bg-white p-8">
        <div className="mb-8 flex flex-col items-center gap-1">
          <div className="mb-2 flex h-10 w-10 items-center justify-center rounded-[10px] bg-primary-navy text-lg font-extrabold text-white">
            z
          </div>
          <h1 className="text-2xl font-bold text-primary-navy">Choose a new password</h1>
        </div>

        {token ? (
          <ResetPasswordForm token={token} />
        ) : (
          <div className="flex flex-col items-center gap-3 text-center">
            <p className="text-sm text-neutral-slate">
              This link is missing its reset code. Open the link from the email exactly as
              it was sent, or ask for a new one.
            </p>
            <Link href="/forgot-password" className="text-[13px] font-bold text-primary-blue">
              Request a new link
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
