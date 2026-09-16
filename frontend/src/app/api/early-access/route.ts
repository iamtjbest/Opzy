import { NextResponse } from "next/server";
import { promises as fs } from "fs";
import path from "path";

export async function POST(request: Request) {
  try {
    const { email } = await request.json();

    if (!email) {
      return NextResponse.json({ error: "Email is required" }, { status: 400 });
    }

    const dataDir = path.join(process.cwd(), "data");
    const filePath = path.join(dataDir, "early_access.csv");

    // Ensure data directory exists
    try {
      await fs.access(dataDir);
    } catch {
      await fs.mkdir(dataDir, { recursive: true });
    }

    const timestamp = new Date().toISOString();
    const csvLine = `"${email}","${timestamp}"\n`;

    await fs.appendFile(filePath, csvLine);

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error("Failed to save email:", error);
    return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
  }
}
