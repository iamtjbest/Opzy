"use client";
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import AppNav from "@/components/AppNav";
import { api, ApiError, OpportunityRead } from "@/lib/api";

export default function OpportunityDetail() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [opp, setOpp] = useState<OpportunityRead | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .getOpportunity(id)
      .then(setOpp)
      .catch((err) => {
        if (err instanceof ApiError && err.status === 401) router.push("/login");
        else if (err instanceof ApiError && err.status === 404) setError("Opportunity not found.");
        else setError("Couldn't reach the server.");
      });
  }, [id, router]);

  return (
    <div className="min-h-screen w-full bg-neutral-mist">
      <AppNav active="Feed" />
      <div className="mx-auto max-w-[700px] px-6 py-12">
        <Link href="/feed" className="text-[13px] font-bold text-neutral-slate hover:text-primary-navy">
          ← Back to feed
        </Link>
        {error && <p className="mt-6 text-sm text-danger-red">{error}</p>}
        {opp && (
          <div className="mt-6 rounded-2xl border border-neutral-border bg-white p-8">
            <h1 className="text-[26px] font-bold text-primary-navy">{opp.title}</h1>
            <p className="mt-1 text-sm text-neutral-slate">
              {opp.organization ?? "Unknown organization"}
              {opp.geography ? ` · ${opp.geography}` : ""}
              {opp.deadline ? ` · Deadline: ${opp.deadline}` : " · Rolling deadline"}
            </p>

            <div className="my-6 h-px w-full bg-neutral-border" />

            <h2 className="text-sm font-bold text-primary-navy">About this opportunity</h2>
            <p className="mt-2 text-sm leading-6 text-neutral-ink">
              {opp.description ?? "No description provided yet."}
            </p>

            {opp.eligibility_notes && (
              <>
                <h2 className="mt-6 text-sm font-bold text-primary-navy">Eligibility</h2>
                <p className="mt-2 text-sm text-neutral-ink">{opp.eligibility_notes}</p>
              </>
            )}

            <div className="my-6 h-px w-full bg-neutral-border" />
            <p className="text-xs text-neutral-slate">
              {opp.verified ? "Verified" : "Not yet verified"}
              {opp.source_url ? ` · Source: ${opp.source_url}` : ""}
            </p>

            <div className="mt-4 flex gap-3">
              {opp.application_url && (
                <a
                  href={opp.application_url}
                  target="_blank"
                  rel="noreferrer"
                  className="rounded-lg bg-primary-navy px-6 py-3 text-sm font-bold text-white hover:bg-[#1c2b52]"
                >
                  Apply on {opp.organization ?? "site"} →
                </a>
              )}
              <button className="rounded-lg border border-neutral-border px-6 py-3 text-sm font-bold text-neutral-ink hover:border-primary-navy">
                Save
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
