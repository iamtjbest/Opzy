"use client";
import { useState } from "react";
import Input from "@/components/Input";
import Button from "@/components/Button";

// `value` is what the API stores (profile_interests.opportunity_type); `label` is display only.
const allTypes = [
  { value: "job", label: "Jobs" },
  { value: "internship", label: "Internships" },
  { value: "scholarship", label: "Scholarships" },
  { value: "fellowship", label: "Fellowships" },
  { value: "grant", label: "Grants" },
  { value: "hackathon", label: "Hackathons" },
  { value: "competition", label: "Competitions" },
];

export default function Onboarding() {
  const [selected, setSelected] = useState(["job", "internship", "hackathon"]);
  const toggle = (t: string) =>
    setSelected((s) => (s.includes(t) ? s.filter((x) => x !== t) : [...s, t]));

  return (
    <div className="flex min-h-screen w-full items-center justify-center bg-neutral-mist px-4 py-16">
      <div className="w-full max-w-[640px] rounded-2xl border border-neutral-border bg-white p-10">
        <h1 className="text-2xl font-bold text-primary-navy">Tell us about you</h1>
        <p className="mt-1 mb-8 text-sm text-neutral-slate">
          Takes about two minutes. This is what we use to find opportunities you actually
          qualify for.
        </p>
        <form className="flex flex-col gap-5">
          <Input label="Education level" placeholder="University student" />
          <Input label="Field of study" placeholder="e.g. Computer Engineering" />
          <Input label="Location" placeholder="e.g. Zaria, Kaduna" />

          <div className="flex flex-col gap-2">
            <span className="text-[13px] font-bold text-neutral-ink">Skills</span>
            <div className="flex flex-wrap items-center gap-2 rounded-lg border border-neutral-border bg-white p-3">
              {["Python", "Public speaking", "Figma"].map((s) => (
                <span key={s} className="rounded-full bg-neutral-mist px-3 py-1.5 text-xs text-neutral-ink">
                  {s}
                </span>
              ))}
              <input
                placeholder="Add another..."
                className="flex-1 min-w-[100px] bg-transparent text-sm text-neutral-slate focus:outline-none"
              />
            </div>
          </div>

          <div className="flex flex-col gap-2">
            <span className="text-[13px] font-bold text-neutral-ink">What are you looking for?</span>
            <div className="flex flex-wrap gap-2.5">
              {allTypes.map(({ value, label }) => {
                const active = selected.includes(value);
                return (
                  <button
                    type="button"
                    key={value}
                    onClick={() => toggle(value)}
                    className={`rounded-full px-4 py-2 text-[13px] transition-colors ${
                      active
                        ? "bg-primary-navy text-white"
                        : "border border-neutral-border bg-white text-neutral-ink hover:border-primary-navy"
                    }`}
                  >
                    {label}
                  </button>
                );
              })}
            </div>
          </div>

          <Button type="submit" href="/feed" className="mt-2 w-full">
            Find my opportunities
          </Button>
          <p className="text-center text-[13px] text-neutral-slate">
            You can always update this later in Settings.
          </p>
        </form>
      </div>
    </div>
  );
}
