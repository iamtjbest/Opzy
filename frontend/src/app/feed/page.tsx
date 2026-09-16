import AppNav from "@/components/AppNav";
import Link from "next/link";
import { opportunities } from "@/lib/opportunities";

const filters = ["All", "Jobs", "Internships", "Scholarships", "Fellowships", "Grants", "Hackathons"];

export default function Feed() {
  return (
    <div className="min-h-screen w-full bg-neutral-mist">
      <AppNav active="Feed" />
      <div className="mx-auto max-w-[1140px] px-6 py-12">
        <h1 className="text-[28px] font-bold text-primary-navy">Your matches</h1>
        <p className="mt-1 text-sm text-neutral-slate">
          {opportunities.length} opportunities found for you, updated today.
        </p>

        <div className="mt-6 flex flex-wrap gap-2.5">
          {filters.map((f) => (
            <span
              key={f}
              className={`rounded-full px-4 py-2 text-[13px] ${
                f === "All" ? "bg-primary-navy text-white" : "border border-neutral-border bg-white text-neutral-ink"
              }`}
            >
              {f}
            </span>
          ))}
        </div>

        <div className="mt-6 flex flex-col gap-4">
          {opportunities.map((o) => (
            <div key={o.id} className="rounded-2xl border border-neutral-border bg-white p-6">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <span className="rounded-lg bg-success-emerald px-3 py-1.5 text-xs font-bold text-white">
                    {o.score}% match
                  </span>
                  <h2 className="text-lg font-bold text-primary-navy">{o.title}</h2>
                </div>
                <button className="rounded-lg border border-neutral-border px-4 py-2 text-xs font-bold text-neutral-ink hover:border-primary-navy">
                  Save
                </button>
              </div>
              <p className="mt-2 text-[13px] text-neutral-slate">
                {o.org} &middot; Deadline: {o.deadline}
              </p>
              <div className="mt-3 flex flex-wrap gap-2">
                {o.reasons.map((r) => (
                  <span key={r} className="rounded-full bg-neutral-mist px-3 py-1.5 text-xs text-neutral-ink">
                    {r}
                  </span>
                ))}
              </div>
              <div className="mt-4 flex items-center justify-between">
                <button className="text-[13px] text-neutral-slate hover:text-primary-navy">Dismiss</button>
                <Link href={`/opportunities/${o.id}`} className="text-[13px] font-bold text-primary-blue">
                  View details →
                </Link>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
