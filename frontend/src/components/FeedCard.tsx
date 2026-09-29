"use client";

import Link from "next/link";
import { useState, useTransition } from "react";

import DismissModal from "@/components/DismissModal";
import { act } from "@/app/actions/opportunities";
import type { FeedItem } from "@/lib/api/types";
import type { DismissReason } from "@/lib/format";
import { CATEGORY_LABELS, deadlineLabel } from "@/lib/format";

/** `today` is computed on the server and passed down, so server and client agree on it. */
export default function FeedCard({ item, today }: { item: FeedItem; today: string }) {
  const { opportunity, score, explanation } = item;
  const [saved, setSaved] = useState(item.user_action === "saved");
  const [dismissed, setDismissed] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [problem, setProblem] = useState<string | null>(null);
  const [, startTransition] = useTransition();

  // Gone from this feed for good; the revalidate will confirm it on the next render.
  if (dismissed) return null;

  function toggleSave() {
    const next = !saved;
    setSaved(next);
    setProblem(null);
    startTransition(async () => {
      const result = await act(opportunity.id, next ? "saved" : "unsaved");
      if (!result.ok) {
        setSaved(!next);
        setProblem("Couldn't save, try again");
      }
    });
  }

  function dismiss(reason: DismissReason) {
    setModalOpen(false);
    setDismissed(true);
    startTransition(async () => {
      const result = await act(opportunity.id, "dismissed", reason);
      if (!result.ok) {
        setDismissed(false);
        setProblem("Couldn't dismiss, try again");
      }
    });
  }

  return (
    <>
      <DismissModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        onDismiss={dismiss}
      />
      <div
        data-testid="feed-card"
        className="rounded-2xl border border-neutral-border bg-white p-6"
      >
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-center gap-3">
            <span className="rounded-lg bg-success-emerald px-3 py-1.5 text-xs font-bold text-white">
              {score}% match
            </span>
            <h2 className="text-lg font-bold text-primary-navy">{opportunity.title}</h2>
          </div>
          <button
            onClick={toggleSave}
            aria-pressed={saved}
            className={`shrink-0 rounded-lg border px-4 py-2 text-xs font-bold transition-colors cursor-pointer ${
              saved
                ? "border-primary-navy bg-primary-navy text-white"
                : "border-neutral-border text-neutral-ink hover:border-primary-navy"
            }`}
          >
            {saved ? "Saved" : "Save"}
          </button>
        </div>

        <p className="mt-2 text-[13px] text-neutral-slate">
          {opportunity.organization ?? "Opzy"} &middot;{" "}
          {deadlineLabel(opportunity.deadline, today)}
        </p>

        {/* The explanation is the product. It replaces the mock's invented reason chips. */}
        <p data-testid="explanation" className="mt-3 text-sm leading-6 text-neutral-ink">
          {explanation}
        </p>

        <div className="mt-3 flex flex-wrap gap-2">
          <span className="rounded-full bg-neutral-mist px-3 py-1.5 text-xs text-neutral-ink">
            {CATEGORY_LABELS[opportunity.category]}
          </span>
          {opportunity.geography && (
            <span className="rounded-full bg-neutral-mist px-3 py-1.5 text-xs text-neutral-ink">
              {opportunity.geography}
            </span>
          )}
        </div>

        {problem && <p className="mt-3 text-xs text-danger-red">{problem}</p>}

        <div className="mt-4 flex items-center justify-between">
          <button
            onClick={() => setModalOpen(true)}
            className="text-[13px] text-neutral-slate transition-colors hover:text-primary-navy cursor-pointer"
          >
            Dismiss
          </button>
          <Link
            href={`/opportunities/${opportunity.id}`}
            className="text-[13px] font-bold text-primary-blue"
          >
            View details →
          </Link>
        </div>
      </div>
    </>
  );
}
