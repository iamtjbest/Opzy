"use client";

import Link from "next/link";
import { useActionState } from "react";

import Input from "@/components/Input";
import SubmitButton from "@/components/SubmitButton";
import { requestPasswordReset } from "@/app/actions/auth";
import { EMPTY_RESET_REQUEST_STATE } from "@/lib/form-state";

export default function ForgotPasswordForm() {
  const [state, formAction] = useActionState(
    requestPasswordReset,
    EMPTY_RESET_REQUEST_STATE,
  );

  if (state.sent) {
    return (
      <div className="flex flex-col items-center gap-3 text-center">
        <span className="flex h-12 w-12 items-center justify-center rounded-full bg-success-emerald/10 text-2xl text-success-emerald">
          ✓
        </span>
        <p className="text-sm text-neutral-slate">
          If that email has an account, a reset link is on its way. It expires in an hour.
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
      <SubmitButton className="w-full" pendingLabel="Sending…">
        Send reset link
      </SubmitButton>
      <Link href="/login" className="text-center text-[13px] text-primary-blue">
        Back to log in
      </Link>
    </form>
  );
}
