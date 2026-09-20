"use server";

import { revalidatePath } from "next/cache";

import { ApiError, apiFetch } from "@/lib/api/server";
import type { ActionState } from "@/lib/api/types";
import type { DismissReason } from "@/lib/format";

export type ActResult =
  | { ok: true; state: ActionState }
  | { ok: false; message: string };

/**
 * Save, unsave, dismiss or mark applied. Repeats are no-ops on the backend, so a
 * double-click is harmless and needs no guarding here.
 */
export async function act(
  opportunityId: string,
  action: "saved" | "unsaved" | "dismissed" | "applied",
  dismissReason?: DismissReason,
): Promise<ActResult> {
  try {
    const state = await apiFetch<ActionState>(
      `/opportunities/${opportunityId}/actions`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action,
          // The backend rejects a reason on anything but a dismiss.
          dismiss_reason: action === "dismissed" ? (dismissReason ?? null) : null,
        }),
      },
    );

    // All three lists are derived from the same rows, so any of them may now be wrong.
    revalidatePath("/feed");
    revalidatePath("/saved");
    revalidatePath("/applications");

    return { ok: true, state };
  } catch (error) {
    if (!(error instanceof ApiError)) throw error;
    return { ok: false, message: error.detail };
  }
}
