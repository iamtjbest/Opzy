import AppNav from "@/components/AppNav";
import CadencePicker from "@/components/CadencePicker";
import DeleteAccountButton from "@/components/DeleteAccountButton";
import LogoutButton from "@/components/LogoutButton";
import ProfileForm from "@/components/ProfileForm";
import { ApiError, apiFetch } from "@/lib/api/server";
import type { NotificationSettings, Profile } from "@/lib/api/types";

async function loadProfile(): Promise<Profile | null> {
  try {
    return await apiFetch<Profile>("/profile");
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) return null;
    throw error;
  }
}

export default async function Settings() {
  const [profile, notifications] = await Promise.all([
    loadProfile(),
    apiFetch<NotificationSettings>("/settings/notifications"),
  ]);

  return (
    <div className="min-h-screen w-full bg-neutral-mist">
      <AppNav active="" />
      <div className="mx-auto max-w-[640px] px-6 py-12">
        <h1 className="text-[28px] font-bold text-primary-navy">Settings</h1>

        <div className="mt-6 rounded-2xl border border-neutral-border bg-white p-8">
          <h2 className="text-base font-bold text-primary-navy">Your profile</h2>
          <p className="mt-1 mb-6 text-[13px] text-neutral-slate">
            This is what your matches are built from.
          </p>
          <ProfileForm profile={profile} redirectTo={null} submitLabel="Save changes" />
        </div>

        <div className="mt-6 rounded-2xl border border-neutral-border bg-white p-8">
          <h2 className="text-base font-bold text-primary-navy">Notifications</h2>
          <p className="mt-4 mb-3 text-[13px] font-bold text-neutral-ink">
            How often do you want to hear from us?
          </p>
          <CadencePicker current={notifications.cadence} />

          <div className="my-6 h-px w-full bg-neutral-border" />

          <h2 className="text-base font-bold text-primary-navy">Account</h2>
          <div className="mt-4 flex items-center gap-4">
            <LogoutButton className="rounded-lg border border-neutral-border px-5 py-2.5 text-[13px] font-bold text-neutral-ink hover:border-primary-navy" />
          </div>

          <div className="my-6 h-px w-full bg-neutral-border" />

          <h2 className="text-base font-bold text-danger-red">Danger Zone</h2>
          <p className="mt-2 text-sm text-neutral-slate">
            Once you delete your account, there is no going back. Please be certain.
          </p>
          <DeleteAccountButton />
        </div>
      </div>
    </div>
  );
}
