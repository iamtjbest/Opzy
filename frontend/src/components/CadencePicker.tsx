"use client";

import { useState, useTransition } from "react";

import { setCadence } from "@/app/actions/settings";
import { CADENCES } from "@/lib/format";
import type { Cadence } from "@/lib/format";

/** Saves on selection — there is one setting here, and a Save button for it is ceremony. */
export default function CadencePicker({ current }: { current: Cadence }) {
  const [selected, setSelected] = useState<Cadence>(current);
  const [problem, setProblem] = useState<string | null>(null);
  const [pending, startTransition] = useTransition();

  function choose(cadence: Cadence) {
    if (cadence === selected) return;
    const previous = selected;
    setSelected(cadence);
    setProblem(null);
    startTransition(async () => {
      const result = await setCadence(cadence);
      if (!result.ok) {
        setSelected(previous);
        setProblem("Couldn't save that, try again");
      }
    });
  }

  return (
    <div className="flex flex-col gap-2" role="radiogroup" aria-label="Email frequency">
      {CADENCES.map(({ value, label, description }) => {
        const active = selected === value;
        return (
          <button
            key={value}
            type="button"
            role="radio"
            aria-checked={active}
            disabled={pending}
            onClick={() => choose(value)}
            className={`flex items-center gap-3 rounded-lg px-4 py-3 text-left transition-colors disabled:opacity-60 cursor-pointer ${
              active ? "bg-neutral-mist" : "border border-neutral-border"
            }`}
          >
            <span
              className={`h-3.5 w-3.5 shrink-0 rounded-full border ${
                active ? "border-primary-navy bg-primary-navy" : "border-neutral-border"
              }`}
            />
            <span>
              <span className="block text-[13px] font-bold text-neutral-ink">{label}</span>
              <span className="block text-xs text-neutral-slate">{description}</span>
            </span>
          </button>
        );
      })}
      {problem && <p className="text-xs text-danger-red">{problem}</p>}
    </div>
  );
}
