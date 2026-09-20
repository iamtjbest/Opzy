import type { Cadence, DismissReason, EducationLevel, OpportunityType } from "@/lib/format";

/** backend/app/schemas/opportunity.py :: OpportunityRead */
export type Opportunity = {
  id: string;
  title: string;
  organization: string | null;
  category: OpportunityType;
  geography: string | null;
  description: string | null;
  /** Null means rolling or unconfirmed. YYYY-MM-DD otherwise. */
  deadline: string | null;
  eligibility_notes: string | null;
  eligible_countries: string[];
  education_levels: string[];
  fields_of_study: string[];
  skills: string[];
  application_url: string | null;
  source_url: string | null;
  quality_rating: number | null;
  verified: boolean;
  status: "active" | "expired" | "removed";
  created_at: string;
  updated_at: string;
};

/** backend/app/schemas/feed.py :: FeedItem — dismissed and applied ones never appear. */
export type FeedItem = {
  opportunity: Opportunity;
  score: number;
  explanation: string;
  user_action: "saved" | null;
};

export type FeedList = {
  items: FeedItem[];
  total: number;
  limit: number;
  offset: number;
};

/** backend/app/schemas/action.py :: ActionState — all three null means no state. */
export type ActionState = {
  opportunity_id: string;
  action: "saved" | "dismissed" | "applied" | null;
  dismiss_reason: DismissReason | null;
  actioned_at: string | null;
};

export type ActionListItem = {
  opportunity: Opportunity;
  actioned_at: string;
};

export type ActionList = {
  items: ActionListItem[];
  total: number;
  limit: number;
  offset: number;
};

/** backend/app/schemas/profile.py :: ProfileRead */
export type Profile = {
  nationality: string | null;
  education_level: EducationLevel | null;
  field_of_study: string | null;
  location: string | null;
  skills: string[];
  interests: OpportunityType[];
  updated_at: string;
};

/**
 * backend/app/schemas/profile.py :: ProfileUpdate. A full replacement — every field is
 * required, and a missing key would silently wipe that field. Send null or [] to clear.
 */
export type ProfileInput = {
  nationality: string | null;
  education_level: EducationLevel | null;
  field_of_study: string | null;
  location: string | null;
  skills: string[];
  interests: OpportunityType[];
};

/** backend/app/schemas/notification_settings.py — channel is read-only until WhatsApp. */
export type NotificationSettings = {
  cadence: Cadence;
  channel: "email" | "whatsapp";
};

export type TokenResponse = {
  access_token: string;
  token_type: string;
};

export type SignupResponse = TokenResponse & {
  user: { id: string; email: string; created_at: string };
};
