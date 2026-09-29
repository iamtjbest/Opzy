import ProfileForm from "@/components/ProfileForm";
import { ApiError, apiFetch } from "@/lib/api/server";
import type { Profile } from "@/lib/api/types";

async function loadProfile(): Promise<Profile | null> {
  try {
    return await apiFetch<Profile>("/profile");
  } catch (error) {
    // 404 is the normal case here: this is the screen for someone who has no profile yet.
    if (error instanceof ApiError && error.status === 404) return null;
    throw error;
  }
}

export default async function Onboarding() {
  const profile = await loadProfile();

  return (
    <div className="flex min-h-screen w-full items-center justify-center bg-neutral-mist px-4 py-16">
      <div className="w-full max-w-[640px] rounded-2xl border border-neutral-border bg-white p-10">
        <h1 className="text-2xl font-bold text-primary-navy">Tell us about you</h1>
        <p className="mt-1 mb-8 text-sm text-neutral-slate">
          Takes about two minutes. This is what we use to find opportunities you actually
          qualify for.
        </p>
        <ProfileForm
          profile={profile}
          redirectTo="/feed"
          submitLabel="Find my opportunities"
        />
        <p className="mt-4 text-center text-[13px] text-neutral-slate">
          You can always update this later in Settings.
        </p>
      </div>
    </div>
  );
}
