"use client";

import { motion, AnimatePresence } from "framer-motion";

import { DISMISS_REASONS } from "@/lib/format";
import type { DismissReason } from "@/lib/format";

export default function DismissModal({
  isOpen,
  onClose,
  onDismiss,
}: {
  isOpen: boolean;
  onClose: () => void;
  onDismiss: (reason: DismissReason) => void;
}) {
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
            <h2 className="text-xl font-bold text-primary-navy">Not for you? Tell us why.</h2>
            <p className="mt-2 text-sm text-neutral-slate">
              This helps us improve your future matches.
            </p>
            <div className="mt-6 flex flex-col gap-3">
              {DISMISS_REASONS.map(({ code, label }) => (
                <button
                  key={code}
                  onClick={() => onDismiss(code)}
                  className="rounded-lg border border-neutral-border px-4 py-3 text-left text-sm font-bold text-neutral-ink hover:border-primary-navy hover:bg-neutral-mist transition-colors cursor-pointer"
                >
                  {label}
                </button>
              ))}
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
