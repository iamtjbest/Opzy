import Link from "next/link";

import LoginForm from "@/components/LoginForm";

export default async function LogIn({
  searchParams,
}: {
  searchParams: Promise<{ next?: string; reset?: string }>;
}) {
  const { next, reset } = await searchParams;

  return (
    <div className="flex min-h-screen w-full items-center justify-center bg-neutral-mist px-4 py-16">
      <div className="w-full max-w-[440px] rounded-2xl border border-neutral-border bg-white p-8">
        <div className="mb-8 flex flex-col items-center gap-1">
          <div className="mb-2 flex h-10 w-10 items-center justify-center rounded-[10px] bg-primary-navy text-lg font-extrabold text-white">
            z
          </div>
          <h1 className="text-2xl font-bold text-primary-navy">Welcome back</h1>
          <p className="text-sm text-neutral-slate">Log in to see what&rsquo;s new.</p>
        </div>
        <LoginForm next={next ?? ""} reset={reset === "1"} />
        <p className="mt-5 text-center text-[13px] text-neutral-slate">
          Don&rsquo;t have an account?{" "}
          <Link href="/signup" className="font-bold text-primary-blue">
            Sign up
          </Link>
        </p>
      </div>
    </div>
  );
}
