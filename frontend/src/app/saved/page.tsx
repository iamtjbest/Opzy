import Link from "next/link";

import AppNav from "@/components/AppNav";
import SavedRow from "@/components/SavedRow";
import { apiFetch } from "@/lib/api/server";
import type { ActionList } from "@/lib/api/types";
import { lagosToday } from "@/lib/format";

const PAGE_SIZE = 50;

export default async function Saved() {
  const saved = await apiFetch<ActionList>(`/saved?limit=${PAGE_SIZE}`);
  const today = lagosToday();

  return (
    <div className="min-h-screen w-full bg-neutral-mist">
      <AppNav active="Saved" />
      <div className="mx-auto max-w-[1140px] px-6 py-12">
        <h1 className="text-[28px] font-bold text-primary-navy">Saved &amp; applications</h1>
        <div className="mt-6 flex gap-8 border-b border-neutral-border">
          <Link
            href="/saved"
            className="border-b-2 border-primary-navy pb-3 text-sm font-bold text-primary-navy"
          >
            Saved ({saved.total})
          </Link>
          <Link
            href="/applications"
            className="pb-3 text-sm font-bold text-neutral-slate hover:text-primary-navy"
          >
            Applications
          </Link>
        </div>

        <div className="mt-6 flex flex-col gap-4">
          {saved.items.length === 0 ? (
            <div className="rounded-xl border border-neutral-border bg-white p-8 text-center">
              <p className="text-neutral-slate">You haven&rsquo;t saved anything yet.</p>
              <Link
                href="/feed"
                className="mt-4 inline-block text-sm font-bold text-primary-blue hover:underline"
              >
                Find opportunities
              </Link>
            </div>
          ) : (
            saved.items.map((item) => (
              <SavedRow key={item.opportunity.id} item={item} today={today} />
            ))
          )}
        </div>
      </div>
    </div>
  );
}
