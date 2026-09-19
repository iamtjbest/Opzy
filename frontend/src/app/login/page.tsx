"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import Button from "@/components/Button";
import { api, setToken, ApiError } from "@/lib/api";

export default function LogIn() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const { access_token } = await api.login(email, password);
      setToken(access_token);
      router.push("/feed");
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        setError("Incorrect email or password.");
      } else {
        setError("Couldn't reach the server. Is the backend running?");
      }
    } finally {
      setLoading(false);
    }
  }

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
        <form onSubmit={handleSubmit} className="flex flex-col gap-5">
          <label className="flex flex-col gap-2">
            <span className="text-[13px] font-bold text-neutral-ink">Email</span>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              className="w-full rounded-lg border border-neutral-border bg-white px-3.5 py-3 text-sm text-neutral-ink placeholder:text-neutral-slate focus:border-primary-blue focus:outline-none"
            />
          </label>
          <div className="flex flex-col gap-2">
            <div className="flex items-center justify-between">
              <span className="text-[13px] font-bold text-neutral-ink">Password</span>
              <Link href="/forgot-password" className="text-[13px] text-primary-blue">
                Forgot password?
              </Link>
            </div>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full rounded-lg border border-neutral-border bg-white px-3.5 py-3 text-sm text-neutral-ink placeholder:text-neutral-slate focus:border-primary-blue focus:outline-none"
            />
          </div>
          {error && <p className="text-[13px] text-danger-red">{error}</p>}
          <Button type="submit" className="mt-1 w-full">
            {loading ? "Logging in..." : "Log in"}
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
