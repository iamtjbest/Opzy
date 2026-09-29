"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";

import DismissModal from "@/components/DismissModal";
import { act } from "@/app/actions/opportunities";
import type { DismissReason } from "@/lib/format";

export default function ActionButtons({
  opportunityId,
  applicationUrl,
  organization,
  initiallySaved,
  initiallyApplied,
}: {
  opportunityId: string;
  applicationUrl: string | null;
  organization: string | null;
  initiallySaved: boolean;
  initiallyApplied: boolean;
}) {
  const router = useRouter();
  const [saved, setSaved] = useState(initiallySaved);
  const [applied, setApplied] = useState(initiallyApplied);
  const [modalOpen, setModalOpen] = useState(false);
  const [problem, setProblem] = useState<string | null>(null);
  const [, startTransition] = useTransition();

  function toggleSave() {
    const next = !saved;
    setSaved(next);
    setProblem(null);
    startTransition(async () => {
      const result = await act(opportunityId, next ? "saved" : "unsaved");
      if (!result.ok) {
        setSaved(!next);
        setProblem("Couldn't save, try again");
      }
    });
  }

  function markApplied() {
    setApplied(true);
    setProblem(null);
    startTransition(async () => {
      const result = await act(opportunityId, "applied");
      if (!result.ok) {
        setApplied(false);
        setProblem("Couldn't record that, try again");
      }
    });
  }

  function dismiss(reason: DismissReason) {
    setModalOpen(false);
    startTransition(async () => {
      const result = await act(opportunityId, "dismissed", reason);
      if (result.ok) {
        // It is out of the feed now, so there is nothing to come back to.
        router.push("/feed");
      } else {
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
      <div className="mt-4 flex flex-wrap gap-3">
        {applicationUrl && (
          <a
            href={applicationUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="rounded-lg bg-primary-navy px-6 py-3 text-sm font-bold text-white transition-colors hover:bg-primary-blue"
          >
            Apply on {organization ?? "their site"} →
          </a>
        )}
        <button
          onClick={toggleSave}
          aria-pressed={saved}
          className={`rounded-lg border px-6 py-3 text-sm font-bold transition-colors cursor-pointer ${
            saved
              ? "border-primary-navy bg-primary-navy text-white"
              : "border-neutral-border text-neutral-ink hover:border-primary-navy"
          }`}
        >
          {saved ? "Saved" : "Save"}
        </button>
        <button
          onClick={markApplied}
          disabled={applied}
          className="rounded-lg border border-neutral-border px-6 py-3 text-sm font-bold text-neutral-ink transition-colors hover:border-primary-navy disabled:cursor-default disabled:border-success-emerald disabled:text-success-emerald cursor-pointer"
        >
          {applied ? "Applied ✓" : "Mark as applied"}
        </button>
      </div>

      {problem && <p className="mt-3 text-xs text-danger-red">{problem}</p>}

      <button
        onClick={() => setModalOpen(true)}
        className="mt-4 text-[13px] text-neutral-slate transition-colors hover:text-primary-navy cursor-pointer"
      >
        Not for you? Tell us why
      </button>
    </>
  );
}
