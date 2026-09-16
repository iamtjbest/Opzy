"use client";

import { useState } from "react";
import Logo from "@/components/Logo";
import Button from "@/components/Button";
import Tag from "@/components/Tag";
import Link from "next/link";
import HeroIllustration from "@/components/HeroIllustration";
import EarlyAccessModal from "@/components/EarlyAccessModal";

const steps = [
  {
    n: 1,
    title: "Tell us about you.",
    body: "Your education, skills, and what you're looking for, in about two minutes, not a full application.",
  },
  {
    n: 2,
    title: "We scan continuously.",
    body: "Jobs, internships, scholarships, fellowships, grants, hackathons, pulled from the places you'd otherwise have to check yourself.",
  },
  {
    n: 3,
    title: "You get matches, explained.",
    body: "Not a list of links, but a short, plain-language reason for every match, including whether you actually qualify.",
  },
];

const categories = [
  "Full-time & part-time jobs",
  "Remote roles",
  "Internships",
  "Scholarships",
  "Fellowships",
  "Grants",
  "Hackathons",
  "Competitions",
];

const reasons = ["Nigeria eligible", "Remote", "Technical background accepted", "Skills match", "Open to students"];

const faqs = [
  {
    q: "Is this just another job board?",
    a: "No. Opzy doesn't just list, it matches. You see a small number of opportunities that fit you, not hundreds you have to filter yourself.",
  },
  {
    q: "Is it free?",
    a: "Yes, to start. A Pro tier is planned for people who want deeper personalization and unlimited tracking, but the core matching experience stays free.",
  },
  {
    q: "How is this different from checking LinkedIn or Googling it myself?",
    a: "Those give you everything. Opzy gives you what you're actually eligible for, from sources you wouldn't otherwise see, explained in plain language, and tells you before the deadline, not after.",
  },
  {
    q: "What if a match isn't relevant?",
    a: "Dismiss it, and tell us why in one tap. That feedback directly improves what you see next.",
  },
];

export default function Home() {
  const [isModalOpen, setIsModalOpen] = useState(false);

  return (
    <div className="flex w-full flex-col bg-white">
      <EarlyAccessModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
      {/* Nav */}
      <div className="fixed top-0 left-1/2 z-10 flex h-20 w-full max-w-[1440px] -translate-x-1/2 items-center justify-between bg-neutral-mist/65 px-6 lg:px-16 backdrop-blur-sm">
        <Logo />
        <div className="flex items-center gap-6">
          <Link href="/about" className="hidden md:block text-sm font-bold text-neutral-slate hover:text-primary-navy">
            About
          </Link>
          <Link href="/pricing" className="hidden md:block text-sm font-bold text-neutral-slate hover:text-primary-navy">
            Pricing
          </Link>
          <Link href="/login" className="text-sm font-bold text-primary-navy hover:text-primary-blue">
            Log in
          </Link>
          <Button onClick={() => setIsModalOpen(true)}>Get Early Access</Button>
        </div>
      </div>

      {/* Hero */}
      <section
        className="flex w-full flex-col lg:flex-row gap-10 lg:gap-14 px-6 lg:px-[150px] pt-32 lg:pt-[200px] pb-16 lg:pb-[120px]"
        style={{
          backgroundImage:
            "linear-gradient(110deg, rgba(16,185,129, 0.2) -10%, rgb(243,245,248) 35%, rgb(243,245,248) 65%, rgba(47,111,237, 0.2) 110%)",
        }}
      >
        <div className="flex flex-1 flex-col items-start gap-6">
          <h1
            className="bg-clip-text text-4xl lg:text-5xl leading-10 lg:leading-[48px] font-extrabold text-transparent"
            style={{
              backgroundImage:
                "linear-gradient(45deg, rgb(20,33,61) 28.7%, rgb(31,36,48) 50%, rgb(47,111,237) 71.3%)",
            }}
          >
            Never miss an
            <br />
            opportunity that fits
            <br />
            you.
          </h1>
          <p className="text-base leading-7 text-neutral-ink">
            Opzy finds the jobs, internships, scholarships, and grants you&rsquo;re actually
            eligible for, the ones scattered across a dozen WhatsApp groups, job boards, and
            pages you don&rsquo;t have time to check every day, and tells you exactly why each
            one fits, before the deadline passes.
          </p>
        </div>
        <div className="flex h-[270px] flex-1 items-center justify-center rounded-2xl bg-neutral-mist p-6">
          <HeroIllustration />
        </div>
      </section>

      {/* Problem */}
      <section
        className="flex w-full flex-col items-center gap-6 px-6 lg:px-[150px] py-16 lg:py-24"
        style={{
          backgroundImage: "linear-gradient(-22deg, rgb(20,33,61) 16.8%, rgb(31,36,48) 83.2%)",
        }}
      >
        <p className="text-center text-sm font-bold tracking-[0.2px] text-neutral-border">
          THE PROBLEM
        </p>
        <h2 className="max-w-[700px] text-center text-[22px] leading-7 font-bold text-white">
          You&rsquo;re not short on opportunities.
          <br />
          You&rsquo;re short on time to find the right ones.
        </h2>
        <p className="max-w-[640px] text-center leading-6 text-neutral-mist">
          Between LinkedIn, Telegram groups, university pages, Twitter, and five different job
          boards, something you actually qualify for is easy to miss. Or you find it three days
          before the deadline and aren&rsquo;t sure if you&rsquo;re even eligible.
        </p>
        <Button variant="outline-dark" onClick={() => setIsModalOpen(true)}>Stop checking ten places. Start with one.</Button>
      </section>

      {/* How it works */}
      <section className="flex w-full items-start bg-neutral-mist px-6 lg:px-[150px] py-16 lg:py-24">
        <div className="flex flex-1 flex-col gap-10 lg:gap-16">
          <div className="flex flex-col items-center gap-2.5 text-center">
            <p className="text-xs font-bold text-primary-blue">THE PROCESS</p>
            <h2 className="text-[22px] font-bold text-neutral-ink">How it Works</h2>
          </div>
          <div className="flex w-full flex-col lg:flex-row gap-7">
            {steps.map((s) => (
              <div
                key={s.n}
                className="flex flex-1 flex-col items-start gap-6 rounded-2xl border-[1.5px] border-neutral-border bg-white px-9 py-8"
              >
                <div
                  className="flex h-11 w-11 items-center justify-center rounded-xl"
                  style={{
                    backgroundImage:
                      "linear-gradient(21deg, rgb(20,33,61) 28.2%, rgb(47,111,237) 71.8%)",
                  }}
                >
                  <span className="text-lg font-bold text-white">{s.n}</span>
                </div>
                <div className="flex flex-col gap-2.5">
                  <p className="text-lg font-bold text-neutral-ink">{s.title}</p>
                  <p className="text-sm leading-5 text-neutral-slate">{s.body}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* What Opzy finds */}
      <section className="flex w-full items-start bg-primary-navy px-6 lg:px-[150px] py-16 lg:py-24">
        <div className="flex flex-1 flex-col items-center gap-[52px]">
          <div className="flex flex-col items-center gap-3 text-center">
            <p className="text-xs font-bold tracking-[2px] text-neutral-slate">WHAT WE TRACK</p>
            <h2 className="text-[22px] font-bold text-white">Everything in one place.</h2>
            <p className="text-neutral-border">
              Opzy scans all the channels you don&rsquo;t have time to monitor.
            </p>
          </div>
          <div className="flex max-w-[820px] flex-col items-center gap-4">
            <div className="flex flex-wrap items-center justify-center gap-[18px]">
              {categories.map((c) => (
                <Tag key={c} tone="on-dark">
                  {c}
                </Tag>
              ))}
            </div>
            <Tag tone="emerald-outline">Starting in Nigeria, built to expand.</Tag>
          </div>
        </div>
      </section>

      {/* Personalization */}
      <section className="flex w-full items-start bg-neutral-mist px-6 lg:px-[150px] py-16 lg:py-24">
        <div className="flex flex-1 flex-col items-center gap-[18px]">
          <p className="text-center text-xs font-bold tracking-[1px] text-neutral-slate">
            HOW MATCHES WORK
          </p>
          <h2 className="text-center text-[22px] font-bold text-primary-navy">
            Every match comes with a reason.
          </h2>
          <p className="text-center text-neutral-slate">
            No score without an explanation attached to it.
          </p>
          <div className="flex w-full max-w-[600px] flex-col items-start gap-2 rounded-2xl border border-neutral-border bg-white px-6 lg:px-8 py-4">
            <div className="rounded-lg bg-success-emerald px-3 py-2">
              <p className="text-[13px] font-bold text-white">92% match</p>
            </div>
            <p className="text-lg font-bold text-primary-navy">Developer Fellowship</p>
            <p className="text-sm text-neutral-slate">Deadline: 14 days</p>
            <p className="text-[13px] font-bold text-neutral-ink">Why it fits:</p>
            <div className="flex flex-wrap items-center gap-3">
              {reasons.map((r) => (
                <Tag key={r} tone="mist">
                  {r}
                </Tag>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Trust */}
      <section className="flex w-full flex-col items-center gap-4 bg-primary-navy px-6 lg:px-[150px] py-12 lg:py-16 text-center">
        <p className="text-sm font-bold tracking-[0.2px] text-primary-blue">TRUST</p>
        <h2 className="text-[28px] font-bold text-white">Checked, not just scraped.</h2>
        <p className="max-w-[600px] text-white/80">
          Every listing shows its source, when it was last verified, and a direct link to apply,
          so you&rsquo;re never guessing whether something is real.
        </p>
        <Button variant="outline-light">See something off? Report it in one tap.</Button>
      </section>

      {/* FAQ */}
      <section className="flex w-full flex-col items-center gap-4 px-6 lg:px-[150px] py-16 lg:py-24">
        <p className="text-xs font-bold tracking-[0.2px] text-neutral-slate">QUESTIONS</p>
        <h2 className="text-[22px] font-bold text-primary-navy">Frequently asked.</h2>
        <div className="flex w-full max-w-[700px] flex-col">
          {faqs.map((f, i) => (
            <div key={f.q} className="flex flex-col gap-1.5 py-4">
              <p className="text-lg font-bold text-primary-navy">{f.q}</p>
              <p className="text-sm leading-5 text-neutral-slate">{f.a}</p>
              {i < faqs.length - 1 && <div className="mt-2.5 h-px w-full bg-neutral-border" />}
            </div>
          ))}
        </div>
      </section>

      {/* Early access */}
      <section className="flex w-full flex-col items-center gap-3 bg-primary-navy px-6 md:px-16 lg:px-[220px] py-16 text-center">
        <h2 className="text-[28px] font-bold text-white">Be first to try Opzy.</h2>
        <p className="text-white/80">
          We&rsquo;re opening early access to a small group first. Sign up and we&rsquo;ll notify
          you as soon as it&rsquo;s ready.
        </p>
        <Button variant="on-dark" onClick={() => setIsModalOpen(true)}>Join early access</Button>
      </section>

      {/* Footer */}
      <footer className="flex w-full flex-col md:flex-row items-center justify-between gap-6 bg-neutral-mist px-6 lg:px-[150px] py-[50px] text-center md:text-left text-sm">
        <p className="font-bold tracking-[0.2px] text-primary-navy">
          Opzy. Never miss an opportunity.
        </p>
        <p className="text-neutral-slate">
          Contact &middot; Twitter/X &middot; Privacy &middot;{" "}
          <Link href="/terms" className="hover:text-primary-navy">Terms</Link>
        </p>
      </footer>
    </div>
  );
}
