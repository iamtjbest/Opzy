import Link from "next/link";
import { notFound } from "next/navigation";

import ActionButtons from "@/components/ActionButtons";
import AppNav from "@/components/AppNav";
import { ApiError, apiFetch } from "@/lib/api/server";
import type { ActionList, Opportunity } from "@/lib/api/types";
import { countryName } from "@/lib/countries";
import { CATEGORY_LABELS, deadlineLabel, lagosToday } from "@/lib/format";

// There is no single-item state endpoint, so state comes from the two lists. Past this
// many, a saved item shows as unsaved — pressing Save again is a no-op on the backend,
// so the worst case is a redundant click. See Decision 7.
const STATE_LOOKUP_LIMIT = 100;

async function isIn(path: string, opportunityId: string): Promise<boolean> {
  const list = await apiFetch<ActionList>(`${path}?limit=${STATE_LOOKUP_LIMIT}`);
  return list.items.some((item) => item.opportunity.id === opportunityId);
}

export default async function OpportunityDetail({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  let opportunity: Opportunity;
  try {
    opportunity = await apiFetch<Opportunity>(`/opportunities/${id}`);
  } catch (error) {
    if (error instanceof ApiError && (error.status === 404 || error.status === 422)) {
      // 422 too: a malformed UUID in the URL is a bad link, not a server fault.
      notFound();
    }
    throw error;
  }

  const [saved, applied] = await Promise.all([
    isIn("/saved", id),
    isIn("/applications", id),
  ]);

  return (
    <div className="min-h-screen w-full bg-neutral-mist">
      <AppNav active="Feed" />
      <div className="mx-auto max-w-[700px] px-6 py-12">
        <Link
          href="/feed"
          className="text-[13px] font-bold text-neutral-slate hover:text-primary-navy"
        >
          ← Back to feed
        </Link>
        <div className="mt-6 rounded-2xl border border-neutral-border bg-white p-8">
          <div className="flex flex-wrap items-center gap-2">
            <span className="inline-block rounded-lg bg-neutral-mist px-3 py-1.5 text-[13px] font-bold text-neutral-ink">
              {CATEGORY_LABELS[opportunity.category]}
            </span>
            {opportunity.verified && (
              <span className="inline-block rounded-full border border-success-emerald/30 bg-success-emerald/10 px-3 py-1.5 text-xs font-bold text-success-emerald">
                Verified
              </span>
            )}
          </div>

          <h1 className="mt-4 text-[26px] font-bold text-primary-navy">
            {opportunity.title}
          </h1>
          <p className="mt-1 text-sm text-neutral-slate">
            {[
              opportunity.organization,
              opportunity.geography,
              deadlineLabel(opportunity.deadline, lagosToday()),
            ]
              .filter(Boolean)
              .join(" · ")}
          </p>

          <div className="my-6 h-px w-full bg-neutral-border" />

          {opportunity.description && (
            <>
              <h2 className="text-sm font-bold text-primary-navy">
                About this opportunity
              </h2>
              <p className="mt-2 text-sm leading-6 whitespace-pre-line text-neutral-ink">
                {opportunity.description}
              </p>
            </>
          )}

          <h2 className="mt-6 text-sm font-bold text-primary-navy">Who it&rsquo;s for</h2>
          <ul className="mt-2 flex flex-col gap-2">
            {opportunity.eligibility_notes && (
              <Bullet>{opportunity.eligibility_notes}</Bullet>
            )}
            <Bullet>
              {opportunity.eligible_countries.length === 0
                ? "Open to any nationality"
                : `Open to: ${opportunity.eligible_countries.map(countryName).join(", ")}`}
            </Bullet>
            {opportunity.education_levels.length > 0 && (
              <Bullet>Education: {opportunity.education_levels.join(", ")}</Bullet>
            )}
            {opportunity.fields_of_study.length > 0 && (
              <Bullet>Fields: {opportunity.fields_of_study.join(", ")}</Bullet>
            )}
            {opportunity.skills.length > 0 && (
              <Bullet>Skills: {opportunity.skills.join(", ")}</Bullet>
            )}
          </ul>

          <div className="my-6 h-px w-full bg-neutral-border" />

          {opportunity.source_url && (
            <p className="text-xs text-neutral-slate">
              Source:{" "}
              <a
                href={opportunity.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary-blue hover:underline"
              >
                {opportunity.source_url}
              </a>
            </p>
          )}

          <ActionButtons
            opportunityId={opportunity.id}
            applicationUrl={opportunity.application_url}
            organization={opportunity.organization}
            initiallySaved={saved}
            initiallyApplied={applied}
          />
        </div>
      </div>
    </div>
  );
}

function Bullet({ children }: { children: React.ReactNode }) {
  return (
    <li className="flex items-start gap-2 text-sm text-neutral-ink">
      <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-success-emerald" />
      <span>{children}</span>
    </li>
  );
}
