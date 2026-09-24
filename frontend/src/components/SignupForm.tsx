"use client";

import Link from "next/link";
import { useActionState } from "react";

import Input from "@/components/Input";
import SubmitButton from "@/components/SubmitButton";
import { signup } from "@/app/actions/auth";
import { EMPTY_SIGNUP_STATE } from "@/lib/form-state";

export default function SignupForm() {
  const [state, formAction] = useActionState(signup, EMPTY_SIGNUP_STATE);

  // Deliberately the same panel whether the address was new or already had an account:
  // the API answers identically for both, and saying "that email is taken" here would
  // hand anyone who asks a way to find out which addresses are registered.
  if (state.sent) {
    return (
      <div className="flex flex-col items-center gap-3 text-center">
        <span className="flex h-12 w-12 items-center justify-center rounded-full bg-success-emerald/10 text-2xl text-success-emerald">
          ✓
        </span>
        <h2 className="text-base font-bold text-primary-navy">Check your email</h2>
        <p className="text-sm text-neutral-slate">
          We&apos;ve sent you a link to confirm your address. It expires in 24 hours.
        </p>
        <Link href="/login" className="text-[13px] font-bold text-primary-blue">
          Back to log in
        </Link>
      </div>
    );
  }

  return (
    <form action={formAction} className="flex flex-col gap-5">
      {state.error && (
        <p className="rounded-lg bg-danger-red/10 px-4 py-3 text-[13px] text-danger-red">
          {state.error}
        </p>
      )}
      <Input
        label="Email"
        name="email"
        placeholder="you@example.com"
        type="email"
        autoComplete="email"
        required
        error={state.fields.email}
      />
      <Input
        label="Password"
        name="password"
        placeholder="••••••••"
        type="password"
        autoComplete="new-password"
        required
        error={state.fields.password}
      />
      <p className="-mt-2 text-xs text-neutral-slate">At least 8 characters.</p>
      <SubmitButton className="mt-1 w-full" pendingLabel="Creating…">
        Create account
      </SubmitButton>
    </form>
  );
}
