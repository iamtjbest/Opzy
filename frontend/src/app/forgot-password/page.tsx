"use client";

import { useState } from "react";
import Link from "next/link";
import Input from "@/components/Input";
import Button from "@/components/Button";

export default function ForgotPassword() {
  const [status, setStatus] = useState<"idle" | "loading" | "success">("idle");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setStatus("loading");
    // Simulate API call
    setTimeout(() => {
      setStatus("success");
    }, 1000);
  };

  return (
    <div className="flex min-h-screen w-full items-center justify-center bg-neutral-mist px-4 py-16">
      <div className="w-full max-w-[440px] rounded-2xl border border-neutral-border bg-white p-8">
        <div className="mb-8 flex flex-col items-center gap-1">
          <div className="mb-2 flex h-10 w-10 items-center justify-center rounded-[10px] bg-primary-navy text-lg font-extrabold text-white">
            z
          </div>
          <h1 className="text-2xl font-bold text-primary-navy">Reset password</h1>
          <p className="text-sm text-center text-neutral-slate">
            Enter the email associated with your account and we&rsquo;ll send you a link to reset your password.
          </p>
        </div>
        
        {status === "success" ? (
          <div className="flex flex-col items-center gap-6">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-success-emerald/10 text-success-emerald">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="20 6 9 17 4 12"></polyline>
              </svg>
            </div>
            <p className="text-center font-bold text-primary-navy">Recovery link sent!</p>
            <p className="text-center text-sm text-neutral-slate">
              Please check your email for instructions on how to reset your password.
            </p>
            <Button href="/login" className="mt-2 w-full justify-center">
              Return to log in
            </Button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="flex flex-col gap-5">
            <Input label="Email" placeholder="you@example.com" type="email" />
            <Button type="submit" className="mt-1 w-full justify-center">
              {status === "loading" ? "Sending..." : "Send recovery link"}
            </Button>
          </form>
        )}
        
        {status !== "success" && (
          <p className="mt-5 text-center text-[13px] text-neutral-slate">
            Remembered your password?{" "}
            <Link href="/login" className="font-bold text-primary-blue">
              Log in
            </Link>
          </p>
        )}
      </div>
    </div>
  );
}
