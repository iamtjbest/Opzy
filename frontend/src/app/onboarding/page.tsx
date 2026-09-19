"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Button from "@/components/Button";
import { api, ApiError, EDUCATION_LEVELS, OPPORTUNITY_TYPE_MAP } from "@/lib/api";

const allTypeLabels = Object.keys(OPPORTUNITY_TYPE_MAP);

export default function Onboarding() {
  const router = useRouter();
  const [nationality, setNationality] = useState("NG");
  const [educationLevel, setEducationLevel] = useState(EDUCATION_LEVELS[1].value);
  const [fieldOfStudy, setFieldOfStudy] = useState("");
  const [location, setLocation] = useState("");
  const [skills, setSkills] = useState<string[]>(["Python", "Public speaking", "Figma"]);
  const [skillInput, setSkillInput] = useState("");
  const [selectedTypes, setSelectedTypes] = useState(["Jobs", "Internships", "Hackathons"]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const toggleType = (t: string) =>
    setSelectedTypes((s) => (s.includes(t) ? s.filter((x) => x !== t) : [...s, t]));

  function addSkill(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter" && skillInput.trim()) {
      e.preventDefault();
      setSkills((s) => [...s, skillInput.trim()]);
      setSkillInput("");
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await api.putProfile({
        nationality: nationality || null,
        education_level: educationLevel || null,
        field_of_study: fieldOfStudy || null,
        location: location || null,
        skills,
        interests: selectedTypes.map((t) => OPPORTUNITY_TYPE_MAP[t]),
      });
      router.push("/feed");
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        router.push("/login");
      } else {
        setError(err instanceof ApiError ? err.message : "Couldn't reach the server.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen w-full items-center justify-center bg-neutral-mist px-4 py-16">
      <div className="w-full max-w-[640px] rounded-2xl border border-neutral-border bg-white p-10">
        <h1 className="text-2xl font-bold text-primary-navy">Tell us about you</h1>
        <p className="mt-1 mb-8 text-sm text-neutral-slate">
          Takes about two minutes. This is what we use to find opportunities you actually
          qualify for.
        </p>
        <form onSubmit={handleSubmit} className="flex flex-col gap-5">
          <label className="flex flex-col gap-2">
            <span className="text-[13px] font-bold text-neutral-ink">Nationality</span>
            <select
              value={nationality}
              onChange={(e) => setNationality(e.target.value)}
              className="w-full rounded-lg border border-neutral-border bg-white px-3.5 py-3 text-sm text-neutral-ink focus:border-primary-blue focus:outline-none"
            >
              <option value="NG">Nigeria</option>
              <option value="GH">Ghana</option>
              <option value="KE">Kenya</option>
              <option value="">Other / prefer not to say</option>
            </select>
          </label>

          <label className="flex flex-col gap-2">
            <span className="text-[13px] font-bold text-neutral-ink">Education level</span>
            <select
              value={educationLevel}
              onChange={(e) => setEducationLevel(e.target.value)}
              className="w-full rounded-lg border border-neutral-border bg-white px-3.5 py-3 text-sm text-neutral-ink focus:border-primary-blue focus:outline-none"
            >
              {EDUCATION_LEVELS.map((l) => (
                <option key={l.value} value={l.value}>
                  {l.label}
                </option>
              ))}
            </select>
          </label>

          <label className="flex flex-col gap-2">
            <span className="text-[13px] font-bold text-neutral-ink">Field of study</span>
            <input
              value={fieldOfStudy}
              onChange={(e) => setFieldOfStudy(e.target.value)}
              placeholder="e.g. Computer Engineering"
              className="w-full rounded-lg border border-neutral-border bg-white px-3.5 py-3 text-sm text-neutral-ink placeholder:text-neutral-slate focus:border-primary-blue focus:outline-none"
            />
          </label>

          <label className="flex flex-col gap-2">
            <span className="text-[13px] font-bold text-neutral-ink">Location</span>
            <input
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="e.g. Zaria, Kaduna"
              className="w-full rounded-lg border border-neutral-border bg-white px-3.5 py-3 text-sm text-neutral-ink placeholder:text-neutral-slate focus:border-primary-blue focus:outline-none"
            />
          </label>

          <div className="flex flex-col gap-2">
            <span className="text-[13px] font-bold text-neutral-ink">Skills</span>
            <div className="flex flex-wrap items-center gap-2 rounded-lg border border-neutral-border bg-white p-3">
              {skills.map((s) => (
                <span
                  key={s}
                  onClick={() => setSkills((sk) => sk.filter((x) => x !== s))}
                  className="cursor-pointer rounded-full bg-neutral-mist px-3 py-1.5 text-xs text-neutral-ink"
                  title="Click to remove"
                >
                  {s} ×
                </span>
              ))}
              <input
                value={skillInput}
                onChange={(e) => setSkillInput(e.target.value)}
                onKeyDown={addSkill}
                placeholder="Type a skill and press Enter"
                className="min-w-[140px] flex-1 bg-transparent text-sm text-neutral-slate focus:outline-none"
              />
            </div>
          </div>

          <div className="flex flex-col gap-2">
            <span className="text-[13px] font-bold text-neutral-ink">What are you looking for?</span>
            <div className="flex flex-wrap gap-2.5">
              {allTypeLabels.map((t) => {
                const active = selectedTypes.includes(t);
                return (
                  <button
                    type="button"
                    key={t}
                    onClick={() => toggleType(t)}
                    className={`rounded-full px-4 py-2 text-[13px] transition-colors ${active
                        ? "bg-primary-navy text-white"
                        : "border border-neutral-border bg-white text-neutral-ink hover:border-primary-navy"
                      }`}
                  >
                    {t}
                  </button>
                );
              })}
            </div>
          </div>

          {error && <p className="text-[13px] text-danger-red">{error}</p>}

          <Button type="submit" className="mt-2 w-full">
            {loading ? "Saving..." : "Find my opportunities"}
          </Button>
          <p className="text-center text-[13px] text-neutral-slate">
            You can always update this later in Settings.
          </p>
        </form>
      </div>
    </div>
  );
}
