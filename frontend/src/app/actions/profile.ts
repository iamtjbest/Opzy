"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

import { ApiError, apiFetch } from "@/lib/api/server";
import type { Profile, ProfileInput } from "@/lib/api/types";
import type { ProfileState } from "@/lib/form-state";
import { EDUCATION_LEVELS, OPPORTUNITY_TYPES } from "@/lib/format";
import type { EducationLevel, OpportunityType } from "@/lib/format";
import { safeNext } from "@/lib/session";

function optionalText(data: FormData, key: string): string | null {
  const value = String(data.get(key) ?? "").trim();
  return value === "" ? null : value;
}

export async function saveProfile(
  _previous: ProfileState,
  data: FormData,
): Promise<ProfileState> {
  const level = String(data.get("education_level") ?? "");
  const skillsRaw = String(data.get("skills") ?? "[]");

  let skills: string[];
  try {
    // The tag input serialises to JSON in a hidden field, so a skill containing a comma
    // survives the round trip.
    const parsed: unknown = JSON.parse(skillsRaw);
    skills = Array.isArray(parsed) ? parsed.map(String) : [];
  } catch {
    skills = [];
  }

  const body: ProfileInput = {
    nationality: optionalText(data, "nationality"),
    education_level: (EDUCATION_LEVELS as readonly string[]).includes(level)
      ? (level as EducationLevel)
      : null,
    field_of_study: optionalText(data, "field_of_study"),
    location: optionalText(data, "location"),
    skills,
    interests: data
      .getAll("interests")
      .map(String)
      .filter((value): value is OpportunityType =>
        (OPPORTUNITY_TYPES as readonly string[]).includes(value),
      ),
  };

  try {
    // PUT replaces the whole profile — every field is sent, every time. Omitting one
    // would wipe it rather than leave it alone.
    await apiFetch<Profile>("/profile", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  } catch (error) {
    if (!(error instanceof ApiError)) throw error;
    return { error: error.detail, fields: error.fields, saved: false };
  }

  // The feed is ranked from the profile, so it is stale the moment this changes.
  revalidatePath("/feed");
  revalidatePath("/settings");

  const destination = safeNext(String(data.get("redirect_to") ?? ""));
  if (destination) redirect(destination);

  return { error: null, fields: {}, saved: true };
}
