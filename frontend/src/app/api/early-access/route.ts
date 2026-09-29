import { NextResponse } from "next/server";
import { promises as fs } from "fs";
import path from "path";

import { pickClientIp, trustedHopsFromEnv } from "@/lib/client-ip";
import {
  MAX_BODY_BYTES,
  MAX_FILE_BYTES,
  PER_IP_LIMIT,
  PER_IP_WINDOW_MS,
  WindowLimiter,
  alreadyListed,
  csvLine,
  normalizeEarlyAccessEmail,
} from "@/lib/early-access";

// Gitignored: this collects real people's addresses, which don't belong in the repo.
const DATA_DIR = path.join(process.cwd(), "data");
const FILE_PATH = path.join(DATA_DIR, "early_access.csv");

const limiter = new WindowLimiter(PER_IP_LIMIT, PER_IP_WINDOW_MS);

function badRequest(error: string) {
  return NextResponse.json({ error }, { status: 400 });
}

async function readList(): Promise<string> {
  try {
    return await fs.readFile(FILE_PATH, "utf8");
  } catch {
    return "";
  }
}

export async function POST(request: Request) {
  const ip =
    pickClientIp(
      request.headers.get("x-forwarded-for"),
      trustedHopsFromEnv(process.env.TRUSTED_PROXY_HOPS),
    ) ?? "unknown";
  if (!limiter.allow(ip, Date.now())) {
    return NextResponse.json(
      { error: "Too many requests. Try again later." },
      { status: 429 },
    );
  }

  const declared = Number(request.headers.get("content-length") ?? "0");
  if (declared > MAX_BODY_BYTES) return badRequest("Request too large");

  let email: string | null;
  try {
    const raw = await request.text();
    if (raw.length > MAX_BODY_BYTES) return badRequest("Request too large");
    email = normalizeEarlyAccessEmail((JSON.parse(raw) as { email?: unknown } | null)?.email);
  } catch {
    return badRequest("Email is required");
  }
  if (!email) return badRequest("Enter a valid email address");

  try {
    await fs.mkdir(DATA_DIR, { recursive: true });
    const existing = await readList();
    // Already on the list: answer as if it were new, so the form can't be used to find
    // out who has signed up.
    if (alreadyListed(existing, email)) return NextResponse.json({ success: true });
    if (Buffer.byteLength(existing) >= MAX_FILE_BYTES) {
      console.error("early_access.csv is full; not recording a new address");
      return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
    }
    await fs.appendFile(FILE_PATH, csvLine(email, new Date()));
    return NextResponse.json({ success: true });
  } catch (error) {
    console.error("Failed to save email:", error);
    return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
  }
}
