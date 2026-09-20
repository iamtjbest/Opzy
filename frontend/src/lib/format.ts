// Every allowed value the UI shows lives here, mirroring backend/app/models/base.py.
// Nothing else in the app re-declares one.

export const LAGOS_TIME_ZONE = "Africa/Lagos";

export const OPPORTUNITY_TYPES = [
  "job",
  "internship",
  "scholarship",
  "fellowship",
  "grant",
  "hackathon",
  "competition",
] as const;
export type OpportunityType = (typeof OPPORTUNITY_TYPES)[number];

// Plural, for the feed's filter chips and the onboarding interest picker.
export const CATEGORY_LABELS: Record<OpportunityType, string> = {
  job: "Jobs",
  internship: "Internships",
  scholarship: "Scholarships",
  fellowship: "Fellowships",
  grant: "Grants",
  hackathon: "Hackathons",
  competition: "Competitions",
};

export const EDUCATION_LEVELS = [
  "secondary",
  "undergraduate",
  "graduate",
  "postgraduate",
] as const;
export type EducationLevel = (typeof EDUCATION_LEVELS)[number];

// Wording from backend/app/models/base.py, so a user picks what the matcher means.
export const EDUCATION_LABELS: Record<EducationLevel, string> = {
  secondary: "Secondary school",
  undergraduate: "Undergraduate (studying now)",
  graduate: "Graduate — first degree or HND, not studying",
  postgraduate: "Postgraduate — master's or PhD",
};

export const DISMISS_REASONS = [
  { code: "not_relevant", label: "Not relevant to my skills" },
  { code: "pay_too_low", label: "Pay is too low" },
  { code: "not_eligible", label: "Not eligible (location, degree)" },
  { code: "not_interested_org", label: "Not interested in this company" },
  { code: "other", label: "Other" },
] as const;
export type DismissReason = (typeof DISMISS_REASONS)[number]["code"];

export const CADENCES = [
  { value: "instant", label: "Instantly", description: "The moment a strong match appears" },
  { value: "daily", label: "Daily", description: "One summary each day" },
  { value: "weekly", label: "Weekly", description: "One summary each week" },
  { value: "off", label: "Off", description: "No emails at all" },
] as const;
export type Cadence = (typeof CADENCES)[number]["value"];

/** Today's date in Lagos, as YYYY-MM-DD. The backend's deadline rule is a Lagos date. */
export function lagosToday(now: Date = new Date()): string {
  // en-CA formats as YYYY-MM-DD, which is what the API sends and what compares correctly.
  return new Intl.DateTimeFormat("en-CA", { timeZone: LAGOS_TIME_ZONE }).format(now);
}

function daysBetween(from: string, to: string): number {
  // Both parsed at UTC midnight, so the difference is whole days with no DST drift.
  const ms = Date.parse(`${to}T00:00:00Z`) - Date.parse(`${from}T00:00:00Z`);
  return Math.round(ms / 86_400_000);
}

/** A human deadline, comparing calendar dates in Lagos. `today` comes from `lagosToday()`. */
export function deadlineLabel(deadline: string | null, today: string): string {
  if (!deadline) return "Rolling";
  const days = daysBetween(today, deadline);
  if (days < 0) return "Closed";
  if (days === 0) return "Closes today";
  if (days === 1) return "Closes tomorrow";
  return `Closes in ${days} days`;
}

// countryName lives in @/lib/countries, next to the generated table it reads. It is not
// here because Intl.DisplayNames disagrees with itself between Node and the browser,
// which breaks hydration in a client component.
