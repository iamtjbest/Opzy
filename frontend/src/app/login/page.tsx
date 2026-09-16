import Link from "next/link";
import Input from "@/components/Input";
import Button from "@/components/Button";

export default function LogIn() {
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
        <form className="flex flex-col gap-5">
          <Input label="Email" placeholder="you@example.com" type="email" />
          <div className="flex flex-col gap-2">
            <div className="flex items-center justify-between">
              <span className="text-[13px] font-bold text-neutral-ink">Password</span>
              <Link href="#" className="text-[13px] text-primary-blue">
                Forgot password?
              </Link>
            </div>
            <input
              type="password"
              placeholder="••••••••"
              className="w-full rounded-lg border border-neutral-border bg-white px-3.5 py-3 text-sm text-neutral-ink placeholder:text-neutral-slate focus:border-primary-blue focus:outline-none"
            />
          </div>
          <Button type="submit" href="/feed" className="mt-1 w-full">
            Log in
          </Button>
        </form>
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
