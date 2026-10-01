import Link from "next/link";

import SignupForm from "@/components/SignupForm";
import Logo from "@/components/Logo";

export default function SignUp() {
  return (
    <div className="flex min-h-screen w-full items-center justify-center bg-neutral-mist px-4 py-16">
      <div className="w-full max-w-[440px] rounded-2xl border border-neutral-border bg-white p-8">
        <div className="mb-8 flex flex-col items-center gap-3">
          <Logo size={40} />
          <h1 className="text-2xl font-bold text-primary-navy">Create your account</h1>
          <p className="text-sm text-neutral-slate">
            Start seeing opportunities that actually fit you.
          </p>
        </div>
        <SignupForm />
        <p className="mt-5 text-center text-[13px] text-neutral-slate">
          Already have an account?{" "}
          <Link href="/login" className="font-bold text-primary-blue">
            Log in
          </Link>
        </p>
      </div>
    </div>
  );
}
