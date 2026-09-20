"use client";

import Link from "next/link";
import { useState, useTransition } from "react";

import { act } from "@/app/actions/opportunities";
import type { ActionListItem } from "@/lib/api/types";
import { deadlineLabel } from "@/lib/format";

export default function SavedRow({
  item,
  today,
}: {
  item: ActionListItem;
  today: string;
}) {
  const { opportunity } = item;
  const [gone, setGone] = useState(false);
  const [problem, setProblem] = useState<string | null>(null);
  const [, startTransition] = useTransition();

  if (gone) return null;

  function run(action: "unsaved" | "applied", failure: string) {
    setGone(true);
    setProblem(null);
    startTransition(async () => {
      const result = await act(opportunity.id, action);
      if (!result.ok) {
        setGone(false);
        setProblem(failure);
      }
    });
  }

  return (
    <div
      data-testid="saved-row"
      className="flex flex-col gap-4 rounded-xl border border-neutral-border bg-white p-5 sm:flex-row sm:items-center sm:justify-between"
    >
      <div>
        <Link
          href={`/opportunities/${opportunity.id}`}
          className="font-bold text-primary-navy hover:underline"
        >
          {opportunity.title}
        </Link>
        <p className="text-[13px] text-neutral-slate">
          {[opportunity.organization, deadlineLabel(opportunity.deadline, today)]
            .filter(Boolean)
            .join(" · ")}
        </p>
        {problem && <p className="mt-1 text-xs text-danger-red">{problem}</p>}
      </div>
      <div className="flex shrink-0 items-center gap-6">
        <button
          onClick={() => run("unsaved", "Couldn't remove, try again")}
          className="text-[13px] text-neutral-slate hover:text-primary-navy cursor-pointer"
        >
          Remove
        </button>
        <button
          onClick={() => run("applied", "Couldn't record that, try again")}
          className="rounded-lg bg-primary-navy px-5 py-2.5 text-[13px] font-bold text-white transition-colors hover:bg-primary-blue cursor-pointer"
        >
          Mark as applied
        </button>
      </div>
    </div>
  );
}
