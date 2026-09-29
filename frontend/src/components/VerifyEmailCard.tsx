"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useActionState, useEffect, useRef, useState } from "react";

import Input from "@/components/Input";
import SubmitButton from "@/components/SubmitButton";
import { resendVerification, verifyEmail } from "@/app/actions/auth";
import { EMPTY_RESET_REQUEST_STATE, type VerifyState } from "@/lib/form-state";

export default function VerifyEmailCard({ token }: { token: string }) {
  const router = useRouter();
  const [state, setState] = useState<VerifyState>({ status: "verifying" });
  // A verification token is single-use, so sending it twice turns a good link into an
  // expired one — and React runs effects twice on mount in development. The *promise* is
  // what's cached, not merely an "already sent" flag: with a flag the second mount skips the
  // call and then have nothing to await, leaving the page stuck on "Confirming…" forever.
  // Keeping the promise means one request per token, and every mount still gets its result.
  const request = useRef<{ token: string; promise: Promise<VerifyState> } | null>(null);

  useEffect(() => {
    if (request.current?.token !== token) {
      request.current = { token, promise: verifyEmail(token) };
    }
    let live = true;
    request.current.promise.then((result) => {
      if (live) setState(result);
    });
    return () => {
      live = false;
    };
  }, [token]);

  if (state.status === "verifying") {
    return (
      <p className="text-center text-sm text-neutral-slate">Confirming your address…</p>
    );
  }

  if (state.status === "verified") {
    return (
      <div className="flex flex-col items-center gap-3 text-center">
        <span className="flex h-12 w-12 items-center justify-center rounded-full bg-success-emerald/10 text-2xl text-success-emerald">
          ✓
        </span>
        <h2 className="text-base font-bold text-primary-navy">You&apos;re all set</h2>
        <p className="text-sm text-neutral-slate">
          Your email is confirmed and you&apos;re logged in.
        </p>
        {/* refresh() so the layout re-reads the session cookie the action just set. */}
        <button
          onClick={() => {
            router.replace("/feed");
            router.refresh();
          }}
          className="mt-1 w-full cursor-pointer rounded-lg bg-primary-navy px-5 py-3 text-[13px] font-bold text-white"
        >
          Continue
        </button>
      </div>
    );
  }

  return <ExpiredPanel message={state.error} />;
}

function ExpiredPanel({ message }: { message: string }) {
  const [state, formAction] = useActionState(
    resendVerification,
    EMPTY_RESET_REQUEST_STATE,
  );

  if (state.sent) {
    return (
      <div className="flex flex-col items-center gap-3 text-center">
        <span className="flex h-12 w-12 items-center justify-center rounded-full bg-success-emerald/10 text-2xl text-success-emerald">
          ✓
        </span>
        <p className="text-sm text-neutral-slate">
          If that address still needs confirming, a new link is on its way.
        </p>
        <Link href="/login" className="text-[13px] font-bold text-primary-blue">
          Back to log in
        </Link>
      </div>
    );
  }

  return (
    <form action={formAction} className="flex flex-col gap-5">
      <p className="rounded-lg bg-danger-red/10 px-4 py-3 text-[13px] text-danger-red">
        {message}
      </p>
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
        Send a new link
      </SubmitButton>
      <Link href="/login" className="text-center text-[13px] text-primary-blue">
        Back to log in
      </Link>
    </form>
  );
}
