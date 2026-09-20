import Link from "next/link";

import AppNav from "@/components/AppNav";
import { apiFetch } from "@/lib/api/server";
import type { ActionList } from "@/lib/api/types";
import { deadlineLabel, lagosToday } from "@/lib/format";

const PAGE_SIZE = 50;

export default async function Applications() {
  const applied = await apiFetch<ActionList>(`/applications?limit=${PAGE_SIZE}`);
  const today = lagosToday();

  return (
    <div className="min-h-screen w-full bg-neutral-mist">
      <AppNav active="Applications" />
      <div className="mx-auto max-w-[1140px] px-6 py-12">
        <h1 className="text-[28px] font-bold text-primary-navy">Saved &amp; applications</h1>
        <div className="mt-6 flex gap-8 border-b border-neutral-border">
          <Link
            href="/saved"
            className="pb-3 text-sm font-bold text-neutral-slate hover:text-primary-navy"
          >
            Saved
          </Link>
          <Link
            href="/applications"
            className="border-b-2 border-primary-navy pb-3 text-sm font-bold text-primary-navy"
          >
            Applications ({applied.total})
          </Link>
        </div>

        <div className="mt-6 flex flex-col gap-4">
          {applied.items.length === 0 ? (
            <div className="rounded-xl border border-neutral-border bg-white p-8 text-center">
              <p className="text-neutral-slate">
                You haven&rsquo;t applied to any opportunities yet.
              </p>
              <Link
                href="/feed"
                className="mt-4 inline-block text-sm font-bold text-primary-blue hover:underline"
              >
                Find opportunities
              </Link>
            </div>
          ) : (
            applied.items.map(({ opportunity, actioned_at }) => (
              <div
                key={opportunity.id}
                className="flex flex-col justify-between gap-4 rounded-xl border border-neutral-border bg-white p-5 sm:flex-row sm:items-center"
              >
                <div className="flex items-center gap-4">
                  <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-lg bg-neutral-mist font-bold text-primary-navy">
                    {(opportunity.organization ?? opportunity.title).charAt(0)}
                  </div>
                  <div>
                    <Link
                      href={`/opportunities/${opportunity.id}`}
                      className="font-bold text-primary-navy hover:underline"
                    >
                      {opportunity.title}
                    </Link>
                    <p className="text-[13px] text-neutral-slate">
                      {[
                        opportunity.organization,
                        `Applied ${new Date(actioned_at).toLocaleDateString("en-GB", {
                          day: "numeric",
                          month: "short",
                          year: "numeric",
                        })}`,
                        deadlineLabel(opportunity.deadline, today),
                      ]
                        .filter(Boolean)
                        .join(" · ")}
                    </p>
                  </div>
                </div>
                <span className="shrink-0 rounded-full bg-success-emerald/10 px-3 py-1 text-xs font-bold text-success-emerald">
                  Application sent
                </span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
