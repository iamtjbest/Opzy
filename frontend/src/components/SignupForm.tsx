"use client";

import { useActionState } from "react";

import Input from "@/components/Input";
import SubmitButton from "@/components/SubmitButton";
import { signup } from "@/app/actions/auth";
import { EMPTY_FORM_STATE } from "@/lib/form-state";

export default function SignupForm() {
  const [state, formAction] = useActionState(signup, EMPTY_FORM_STATE);

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
