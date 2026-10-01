"use client";

import Link from "next/link";
import { useActionState, useState } from "react";

import Input from "@/components/Input";
import PasswordVisibilityToggle from "@/components/PasswordVisibilityToggle";
import SubmitButton from "@/components/SubmitButton";
import { login } from "@/app/actions/auth";
import { EMPTY_FORM_STATE } from "@/lib/form-state";

export default function LoginForm({ next, reset }: { next: string; reset: boolean }) {
  const [state, formAction] = useActionState(login, EMPTY_FORM_STATE);
  const [passwordVisible, setPasswordVisible] = useState(false);

  return (
    <form action={formAction} className="flex flex-col gap-5">
      {reset && (
        <p className="rounded-lg bg-success-emerald/10 px-4 py-3 text-[13px] text-success-emerald">
          Your password has been updated. Log in with it.
        </p>
      )}
      {state.error && (
        <p className="rounded-lg bg-danger-red/10 px-4 py-3 text-[13px] text-danger-red">
          {state.error}
        </p>
      )}
      <input type="hidden" name="next" value={next} />
      <Input
        label="Email"
        name="email"
        placeholder="you@example.com"
        type="email"
        autoComplete="email"
        required
        error={state.fields.email}
      />
      <div className="flex flex-col gap-2">
        <div className="flex items-center justify-between">
          {/* A real label, not a span: the field is laid out by hand here (to fit the
              "Forgot password?" link beside it) rather than through Input, and without
              htmlFor it has no accessible name at all. */}
          <label htmlFor="login-password" className="text-[13px] font-bold text-neutral-ink">
            Password
          </label>
          <Link href="/forgot-password" className="text-[13px] text-primary-blue">
            Forgot password?
          </Link>
        </div>
        <span className="relative flex items-center">
          <input
            id="login-password"
            type={passwordVisible ? "text" : "password"}
            name="password"
            placeholder="••••••••"
            autoComplete="current-password"
            required
            className="w-full rounded-lg border border-neutral-border bg-white px-3.5 py-3 pr-10 text-sm text-neutral-ink placeholder:text-neutral-slate focus:border-primary-blue focus:outline-none"
          />
          <span className="absolute right-3.5">
            <PasswordVisibilityToggle
              visible={passwordVisible}
              onToggle={() => setPasswordVisible((v) => !v)}
            />
          </span>
        </span>
      </div>
      <SubmitButton className="mt-1 w-full" pendingLabel="Logging in…">
        Log in
      </SubmitButton>
    </form>
  );
}
