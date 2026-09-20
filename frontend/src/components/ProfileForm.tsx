"use client";

import { useActionState, useState } from "react";

import Input from "@/components/Input";
import SubmitButton from "@/components/SubmitButton";
import { saveProfile } from "@/app/actions/profile";
import type { Profile } from "@/lib/api/types";
import { COUNTRY_CODES } from "@/lib/countries";
import { EMPTY_PROFILE_STATE } from "@/lib/form-state";
import {
  CATEGORY_LABELS,
  EDUCATION_LABELS,
  EDUCATION_LEVELS,
  OPPORTUNITY_TYPES,
  countryName,
} from "@/lib/format";

// Mirrors backend/app/schemas/profile.py. The backend still has the final say; these only
// stop an obviously-doomed request leaving the browser. The 100-character limit on the
// free-text fields is deliberately *not* enforced here — a silent truncation would lose
// what someone typed, and the backend's 422 says so plainly instead.
const MAX_SKILLS = 30;
const MAX_SKILL_LENGTH = 50;

export default function ProfileForm({
  profile,
  redirectTo,
  submitLabel,
}: {
  profile: Profile | null;
  redirectTo: string | null;
  submitLabel: string;
}) {
  const [state, formAction] = useActionState(saveProfile, EMPTY_PROFILE_STATE);
  const [skills, setSkills] = useState<string[]>(profile?.skills ?? []);
  const [draft, setDraft] = useState("");
  const [interests, setInterests] = useState<string[]>(profile?.interests ?? []);

  function addSkill() {
    // Lowercased to match the backend, which does the same so "Python" and "python" are
    // one skill.
    const skill = draft.trim().toLowerCase().slice(0, MAX_SKILL_LENGTH);
    if (skill && skills.length < MAX_SKILLS && !skills.includes(skill)) {
      setSkills([...skills, skill]);
    }
    setDraft("");
  }

  function toggleInterest(type: string) {
    setInterests((current) =>
      current.includes(type) ? current.filter((t) => t !== type) : [...current, type],
    );
  }

  return (
    <form action={formAction} className="flex flex-col gap-5">
      {state.error && (
        <p className="rounded-lg bg-danger-red/10 px-4 py-3 text-[13px] text-danger-red">
          {state.error}
        </p>
      )}
      {state.saved && (
        <p className="rounded-lg bg-success-emerald/10 px-4 py-3 text-[13px] text-success-emerald">
          Saved. Your feed has been updated.
        </p>
      )}

      <input type="hidden" name="redirect_to" value={redirectTo ?? ""} />
      <input type="hidden" name="skills" value={JSON.stringify(skills)} />

      <label className="flex flex-col gap-2">
        <span className="text-[13px] font-bold text-neutral-ink">Nationality</span>
        <select
          name="nationality"
          defaultValue={profile?.nationality ?? ""}
          className="w-full rounded-lg border border-neutral-border bg-white px-3.5 py-3 text-sm text-neutral-ink focus:border-primary-blue focus:outline-none"
        >
          <option value="">Prefer not to say</option>
          {COUNTRY_CODES.map((code) => (
            <option key={code} value={code}>
              {countryName(code)}
            </option>
          ))}
        </select>
        {state.fields.nationality && (
          <span className="text-xs text-danger-red">{state.fields.nationality}</span>
        )}
      </label>

      <label className="flex flex-col gap-2">
        <span className="text-[13px] font-bold text-neutral-ink">Education level</span>
        <select
          name="education_level"
          defaultValue={profile?.education_level ?? ""}
          className="w-full rounded-lg border border-neutral-border bg-white px-3.5 py-3 text-sm text-neutral-ink focus:border-primary-blue focus:outline-none"
        >
          <option value="">Prefer not to say</option>
          {EDUCATION_LEVELS.map((level) => (
            <option key={level} value={level}>
              {EDUCATION_LABELS[level]}
            </option>
          ))}
        </select>
        {state.fields.education_level && (
          <span className="text-xs text-danger-red">{state.fields.education_level}</span>
        )}
      </label>

      <Input
        label="Field of study"
        name="field_of_study"
        placeholder="e.g. Computer Engineering"
        defaultValue={profile?.field_of_study ?? ""}
        error={state.fields.field_of_study}
      />
      <Input
        label="Location"
        name="location"
        placeholder="e.g. Zaria, Kaduna"
        defaultValue={profile?.location ?? ""}
        error={state.fields.location}
      />

      <div className="flex flex-col gap-2">
        <span className="text-[13px] font-bold text-neutral-ink">Skills</span>
        <div className="flex flex-wrap items-center gap-2 rounded-lg border border-neutral-border bg-white p-3">
          {skills.map((skill) => (
            <button
              type="button"
              key={skill}
              onClick={() => setSkills(skills.filter((s) => s !== skill))}
              aria-label={`Remove ${skill}`}
              className="rounded-full bg-neutral-mist px-3 py-1.5 text-xs text-neutral-ink hover:bg-neutral-border"
            >
              {skill} ×
            </button>
          ))}
          <input
            aria-label="Add a skill"
            value={draft}
            maxLength={MAX_SKILL_LENGTH}
            onChange={(e) => setDraft(e.target.value)}
            onKeyDown={(e) => {
              // Enter must not submit the whole form from inside a tag input.
              if (e.key === "Enter" || e.key === ",") {
                e.preventDefault();
                addSkill();
              }
            }}
            onBlur={addSkill}
            placeholder={skills.length >= MAX_SKILLS ? "That's the maximum" : "Add another…"}
            disabled={skills.length >= MAX_SKILLS}
            className="min-w-[120px] flex-1 bg-transparent text-sm text-neutral-ink placeholder:text-neutral-slate focus:outline-none"
          />
        </div>
        <span className="text-xs text-neutral-slate">
          {skills.length} of {MAX_SKILLS}. Press Enter after each one.
        </span>
        {state.fields.skills && (
          <span className="text-xs text-danger-red">{state.fields.skills}</span>
        )}
      </div>

      <div className="flex flex-col gap-2">
        <span className="text-[13px] font-bold text-neutral-ink">
          What are you looking for?
        </span>
        <div className="flex flex-wrap gap-2.5">
          {OPPORTUNITY_TYPES.map((type) => {
            const active = interests.includes(type);
            return (
              <button
                type="button"
                key={type}
                aria-pressed={active}
                onClick={() => toggleInterest(type)}
                className={`rounded-full px-4 py-2 text-[13px] transition-colors ${
                  active
                    ? "bg-primary-navy text-white"
                    : "border border-neutral-border bg-white text-neutral-ink hover:border-primary-navy"
                }`}
              >
                {CATEGORY_LABELS[type]}
              </button>
            );
          })}
        </div>
        {interests.map((type) => (
          <input key={type} type="hidden" name="interests" value={type} />
        ))}
        {state.fields.interests && (
          <span className="text-xs text-danger-red">{state.fields.interests}</span>
        )}
      </div>

      <SubmitButton className="mt-2 w-full" pendingLabel="Saving…">
        {submitLabel}
      </SubmitButton>
    </form>
  );
}
