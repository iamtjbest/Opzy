"use client";

import Link from "next/link";
import { useActionState } from "react";

import Input from "@/components/Input";
import SubmitButton from "@/components/SubmitButton";
import { confirmPasswordReset } from "@/app/actions/auth";
import { EMPTY_FORM_STATE } from "@/lib/form-state";

export default function ResetPasswordForm({ token }: { token: string }) {
  const [state, formAction] = useActionState(confirmPasswordReset, EMPTY_FORM_STATE);

  return (
    <form action={formAction} className="flex flex-col gap-5">
      {state.error && (
        <div className="rounded-lg bg-danger-red/10 px-4 py-3 text-[13px] text-danger-red">
          <p>{state.error}</p>
          <Link href="/forgot-password" className="mt-1 inline-block font-bold underline">
            Request a new link
          </Link>
        </div>
      )}
      <input type="hidden" name="token" value={token} />
      <Input
        label="New password"
        name="password"
        placeholder="••••••••"
        type="password"
        autoComplete="new-password"
        required
        error={state.fields.new_password}
      />
      <Input
        label="Confirm new password"
        name="confirm"
        placeholder="••••••••"
        type="password"
        autoComplete="new-password"
        required
        error={state.fields.confirm}
      />
      <p className="-mt-2 text-xs text-neutral-slate">At least 8 characters.</p>
      <SubmitButton className="w-full" pendingLabel="Updating…">
        Set new password
      </SubmitButton>
    </form>
  );
}
