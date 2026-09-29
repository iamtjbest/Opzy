"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

export default function EarlyAccessModal({
  isOpen,
  onClose,
}: {
  isOpen: boolean;
  onClose: () => void;
}) {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;

    setStatus("loading");
    try {
      const res = await fetch("/api/early-access", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });

      if (res.ok) {
        setStatus("success");
        setTimeout(() => {
          onClose();
          setStatus("idle");
          setEmail("");
        }, 2000);
      } else {
        setStatus("error");
      }
    } catch {
      setStatus("error");
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="absolute inset-0 bg-primary-navy/40 backdrop-blur-sm"
          />
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className="relative z-10 w-full max-w-md overflow-hidden rounded-2xl bg-white p-8 shadow-2xl"
          >
            <button
              onClick={onClose}
              className="absolute right-4 top-4 text-neutral-slate hover:text-primary-navy transition-colors"
            >
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </button>
            <h2 className="text-2xl font-bold text-primary-navy">Join Early Access</h2>
            <p className="mt-2 text-neutral-slate">
              Enter your email to get notified as soon as Opzy is ready for you.
            </p>
            <form onSubmit={handleSubmit} className="mt-6 flex flex-col gap-4">
              <input
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full rounded-lg border border-neutral-border bg-neutral-mist px-4 py-3 text-neutral-ink placeholder:text-neutral-slate focus:border-primary-blue focus:outline-none focus:ring-1 focus:ring-primary-blue transition-all"
              />
              <button
                type="submit"
                disabled={status === "loading" || status === "success"}
                className="inline-flex w-full items-center justify-center rounded-lg bg-primary-navy px-5 py-3 font-bold text-white transition-all hover:bg-primary-blue active:scale-95 disabled:opacity-70 disabled:active:scale-100"
              >
                {status === "loading" ? "Submitting..." : status === "success" ? "You're in!" : "Get Access"}
              </button>
              {status === "error" && (
                <p className="text-center text-sm text-danger-red">Something went wrong. Please try again.</p>
              )}
            </form>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
