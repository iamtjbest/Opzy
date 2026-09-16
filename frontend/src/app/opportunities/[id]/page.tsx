import Link from "next/link";
import AppNav from "@/components/AppNav";
import { opportunities } from "@/lib/opportunities";
import { notFound } from "next/navigation";

export default async function OpportunityDetail({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const opp = opportunities.find((o) => o.id === id);
  if (!opp) return notFound();

  return (
    <div className="min-h-screen w-full bg-neutral-mist">
      <AppNav active="Feed" />
      <div className="mx-auto max-w-[700px] px-6 py-12">
        <Link href="/feed" className="text-[13px] font-bold text-neutral-slate hover:text-primary-navy">
          ← Back to feed
        </Link>
        <div className="mt-6 rounded-2xl border border-neutral-border bg-white p-8">
          <span className="inline-block rounded-lg bg-success-emerald px-3 py-1.5 text-[13px] font-bold text-white">
            {opp.score}% match
          </span>
          <h1 className="mt-4 text-[26px] font-bold text-primary-navy">{opp.title}</h1>
          <p className="mt-1 text-sm text-neutral-slate">
            {opp.org} &middot; {opp.remote ? "Remote" : "On-site"} &middot; Deadline in {opp.deadline}
          </p>

          <div className="my-6 h-px w-full bg-neutral-border" />

          <h2 className="text-sm font-bold text-primary-navy">About this opportunity</h2>
          <p className="mt-2 text-sm leading-6 text-neutral-ink">{opp.description}</p>

          <h2 className="mt-6 text-sm font-bold text-primary-navy">Why you&rsquo;re eligible</h2>
          <ul className="mt-2 flex flex-col gap-2">
            {opp.eligibility.map((e) => (
              <li key={e} className="flex items-start gap-2 text-sm text-neutral-ink">
                <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-success-emerald" />
                {e}
              </li>
            ))}
          </ul>

          <div className="my-6 h-px w-full bg-neutral-border" />
          <p className="text-xs text-neutral-slate">
            Verified from {opp.source}. Last checked today.
          </p>

          <div className="mt-4 flex gap-3">
            <button className="rounded-lg bg-primary-navy px-6 py-3 text-sm font-bold text-white hover:bg-[#1c2b52]">
              Apply on {opp.org} →
            </button>
            <button className="rounded-lg border border-neutral-border px-6 py-3 text-sm font-bold text-neutral-ink hover:border-primary-navy">
              Save
            </button>
          </div>
          <button className="mt-4 text-[13px] text-neutral-slate hover:text-primary-navy">
            Not for you? Tell us why
          </button>
        </div>
      </div>
    </div>
  );
}
