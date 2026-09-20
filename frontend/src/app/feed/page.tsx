import Link from "next/link";
import { redirect } from "next/navigation";

import AppNav from "@/components/AppNav";
import FeedCard from "@/components/FeedCard";
import { ApiError, apiFetch } from "@/lib/api/server";
import type { FeedList } from "@/lib/api/types";
import { CATEGORY_LABELS, OPPORTUNITY_TYPES, lagosToday } from "@/lib/format";
import type { OpportunityType } from "@/lib/format";

const PAGE_SIZE = 50;

export default async function Feed({
  searchParams,
}: {
  searchParams: Promise<{ category?: string }>;
}) {
  const { category } = await searchParams;
  const active = (OPPORTUNITY_TYPES as readonly string[]).includes(category ?? "")
    ? (category as OpportunityType)
    : null;

  const query = new URLSearchParams({ limit: String(PAGE_SIZE) });
  if (active) query.set("category", active);

  let feed: FeedList;
  try {
    feed = await apiFetch<FeedList>(`/feed?${query}`);
  } catch (error) {
    // 404 from /feed means no profile yet — the same signal GET /profile gives.
    if (error instanceof ApiError && error.status === 404) redirect("/onboarding");
    throw error;
  }

  const today = lagosToday();

  return (
    <div className="min-h-screen w-full bg-neutral-mist">
      <AppNav active="Feed" />
      <div className="mx-auto max-w-[1140px] px-6 py-12">
        <h1 className="text-[28px] font-bold text-primary-navy">Your matches</h1>
        <p className="mt-1 text-sm text-neutral-slate">
          {feed.total} {feed.total === 1 ? "opportunity" : "opportunities"} found for you,
          updated today.
        </p>

        <div className="mt-6 flex flex-wrap gap-2.5">
          <FilterChip href="/feed" label="All" active={active === null} />
          {OPPORTUNITY_TYPES.map((type) => (
            <FilterChip
              key={type}
              href={`/feed?category=${type}`}
              label={CATEGORY_LABELS[type]}
              active={active === type}
            />
          ))}
        </div>

        <div className="mt-6 flex flex-col gap-4">
          {feed.items.length === 0 ? (
            <div className="rounded-2xl border border-neutral-border bg-white p-8 text-center">
              <p className="text-neutral-slate">
                Nothing here yet.{" "}
                {active
                  ? "Try another category, or clear the filter."
                  : "Widen what you're looking for in Settings and we'll keep looking."}
              </p>
              <Link
                href="/settings"
                className="mt-4 inline-block text-sm font-bold text-primary-blue hover:underline"
              >
                Update your profile
              </Link>
            </div>
          ) : (
            feed.items.map((item) => (
              <FeedCard key={item.opportunity.id} item={item} today={today} />
            ))
          )}
        </div>

        {feed.total > feed.items.length && (
          <p className="mt-6 text-center text-[13px] text-neutral-slate">
            Showing the top {feed.items.length} of {feed.total}.
          </p>
        )}
      </div>
    </div>
  );
}

function FilterChip({
  href,
  label,
  active,
}: {
  href: string;
  label: string;
  active: boolean;
}) {
  return (
    <Link
      href={href}
      className={`rounded-full px-4 py-2 text-[13px] transition-colors ${
        active
          ? "border border-primary-navy bg-primary-navy text-white"
          : "border border-neutral-border bg-white text-neutral-ink hover:border-primary-navy"
      }`}
    >
      {label}
    </Link>
  );
}
