"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import AppNav from "@/components/AppNav";
import { api, ApiError, FeedItem } from "@/lib/api";

export default function Feed() {
  const router = useRouter();
  const [items, setItems] = useState<FeedItem[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .getFeed()
      .then((data) => setItems(data.items))
      .catch((err) => {
        if (err instanceof ApiError && err.status === 401) {
          router.push("/login");
        } else if (err instanceof ApiError && err.status === 404) {
          router.push("/onboarding");
        } else {
          setError("Couldn't reach the server. Is the backend running?");
        }
      });
  }, [router]);

  return (
    <div className="min-h-screen w-full bg-neutral-mist">
      <AppNav active="Feed" />
      <div className="mx-auto max-w-[1140px] px-6 py-12">
        <h1 className="text-[28px] font-bold text-primary-navy">Your matches</h1>
        <p className="mt-1 text-sm text-neutral-slate">
          {items ? `${items.length} opportunities found for you, updated today.` : "Loading..."}
        </p>

        {error && <p className="mt-6 text-sm text-danger-red">{error}</p>}

        <div className="mt-6 flex flex-col gap-4">
          {items?.length === 0 && (
            <p className="text-sm text-neutral-slate">
              No matches yet, check back soon or widen what you&rsquo;re looking for in your
              profile.
            </p>
          )}
          {items?.map((item) => (
            <div key={item.opportunity.id} className="rounded-2xl border border-neutral-border bg-white p-6">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <span className="rounded-lg bg-success-emerald px-3 py-1.5 text-xs font-bold text-white">
                    {item.score}% match
                  </span>
                  <h2 className="text-lg font-bold text-primary-navy">{item.opportunity.title}</h2>
                </div>
                <button className="rounded-lg border border-neutral-border px-4 py-2 text-xs font-bold text-neutral-ink hover:border-primary-navy">
                  Save
                </button>
              </div>
              <p className="mt-2 text-[13px] text-neutral-slate">
                {item.opportunity.organization ?? "Unknown organization"}
                {item.opportunity.deadline ? ` · Deadline: ${item.opportunity.deadline}` : " · Rolling deadline"}
              </p>
              <p className="mt-3 text-sm text-neutral-ink">{item.explanation}</p>
              <div className="mt-4 flex items-center justify-between">
                <button className="text-[13px] text-neutral-slate hover:text-primary-navy">Dismiss</button>
                <Link href={`/opportunities/${item.opportunity.id}`} className="text-[13px] font-bold text-primary-blue">
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
