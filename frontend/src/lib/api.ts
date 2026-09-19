const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const TOKEN_KEY = "opzy_token";

export function getToken(): string | null {
    if (typeof window === "undefined") return null;
    return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string) {
    localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
    localStorage.removeItem(TOKEN_KEY);
}

export class ApiError extends Error {
    status: number;
    constructor(status: number, message: string) {
        super(message);
        this.status = status;
    }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
    const token = getToken();
    const headers = new Headers(options.headers);
    if (token) headers.set("Authorization", `Bearer ${token}`);

    const res = await fetch(`${API_URL}${path}`, { ...options, headers });
    if (!res.ok) {
        const body = await res.json().catch(() => null);
        const message = body?.detail ?? `Request failed with status ${res.status}`;
        throw new ApiError(res.status, typeof message === "string" ? message : JSON.stringify(message));
    }
    if (res.status === 204) return null as T;
    return res.json();
}

// Types matching backend/app/schemas exactly
export type UserRead = {
    id: string;
    email: string;
    notification_cadence: string;
    notification_channel: string;
    created_at: string;
};

export type OpportunityRead = {
    id: string;
    title: string;
    organization: string | null;
    category: string;
    geography: string | null;
    description: string | null;
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
    status: string;
};

export type FeedItem = {
    opportunity: OpportunityRead;
    score: number;
    explanation: string;
};

export type ProfileUpdate = {
    nationality: string | null;
    education_level: string | null;
    field_of_study: string | null;
    location: string | null;
    skills: string[];
    interests: string[];
};

export const api = {
    signup: (email: string, password: string) =>
        request<{ access_token: string; user: UserRead }>("/auth/signup", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password }),
        }),

    login: (email: string, password: string) => {
        const form = new URLSearchParams();
        form.set("username", email);
        form.set("password", password);
        return request<{ access_token: string }>("/auth/login", {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: form.toString(),
        });
    },

    me: () => request<UserRead>("/auth/me"),

    getProfile: () => request<ProfileUpdate & { updated_at: string }>("/profile"),

    putProfile: (data: ProfileUpdate) =>
        request<ProfileUpdate & { updated_at: string }>("/profile", {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
        }),

    getFeed: () => request<{ items: FeedItem[]; total: number }>("/feed"),

    getOpportunity: (id: string) => request<OpportunityRead>(`/opportunities/${id}`),
};

// UI label <-> API value maps, since the backend only accepts these exact strings
export const OPPORTUNITY_TYPE_MAP: Record<string, string> = {
    Jobs: "job",
    Internships: "internship",
    Scholarships: "scholarship",
    Fellowships: "fellowship",
    Grants: "grant",
    Hackathons: "hackathon",
    Competitions: "competition",
};

export const EDUCATION_LEVELS: { value: string; label: string }[] = [
    { value: "secondary", label: "Secondary school" },
    { value: "undergraduate", label: "University student (undergraduate)" },
    { value: "graduate", label: "Graduate (degree completed)" },
    { value: "postgraduate", label: "Postgraduate (Master's / PhD)" },
];
