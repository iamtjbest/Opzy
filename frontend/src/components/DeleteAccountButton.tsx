"use client";

import { useActionState, useState } from "react";

import Input from "@/components/Input";
import SubmitButton from "@/components/SubmitButton";
import { deleteAccount } from "@/app/actions/auth";
import { EMPTY_FORM_STATE } from "@/lib/form-state";

const DANGER_BUTTON =
  "rounded-lg border border-danger-red px-5 py-2.5 text-[13px] font-bold text-danger-red transition-colors hover:bg-danger-red hover:text-white cursor-pointer";

export default function DeleteAccountButton() {
  const [confirming, setConfirming] = useState(false);
  const [state, formAction] = useActionState(deleteAccount, EMPTY_FORM_STATE);

  if (!confirming) {
    return (
      <button onClick={() => setConfirming(true)} className={`mt-4 ${DANGER_BUTTON}`}>
        Delete Account
      </button>
    );
  }

  return (
    <form
      action={formAction}
      className="mt-4 flex flex-col gap-4 rounded-lg border border-danger-red/40 bg-danger-red/5 p-5"
    >
      <p className="text-[13px] font-bold text-danger-red">
        This deletes your profile, your saved opportunities and your applications. It
        can&apos;t be undone.
      </p>
      {state.error && (
        <p className="rounded-lg bg-danger-red/10 px-4 py-3 text-[13px] text-danger-red">
          {state.error}
        </p>
      )}
      {/* The password, not just a click: a borrowed session shouldn't be able to do this. */}
      <Input
        label="Confirm your password"
        name="password"
        placeholder="••••••••"
        type="password"
        autoComplete="current-password"
        required
        error={state.fields.password}
      />
      <div className="flex items-center gap-3">
        <SubmitButton className={DANGER_BUTTON} pendingLabel="Deleting…">
          Delete my account for good
        </SubmitButton>
        <button
          type="button"
          onClick={() => setConfirming(false)}
          className="cursor-pointer rounded-lg border border-neutral-border px-5 py-2.5 text-[13px] font-bold text-neutral-ink hover:border-primary-navy"
        >
          Cancel
        </button>
      </div>
    </form>
  );
}
