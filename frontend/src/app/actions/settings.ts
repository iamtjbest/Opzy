"use server";

import { revalidatePath } from "next/cache";

import { ApiError, apiFetch } from "@/lib/api/server";
import type { NotificationSettings } from "@/lib/api/types";
import type { Cadence } from "@/lib/format";

export async function setCadence(
  cadence: Cadence,
): Promise<{ ok: boolean; message?: string }> {
  try {
    // PUT takes the cadence alone: the channel is read-only until WhatsApp exists.
    await apiFetch<NotificationSettings>("/settings/notifications", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ cadence }),
    });
  } catch (error) {
    if (!(error instanceof ApiError)) throw error;
    return { ok: false, message: error.detail };
  }

  revalidatePath("/settings");
  return { ok: true };
}
