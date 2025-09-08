// /app/api/assemblyai/route.ts
import { NextResponse } from "next/server";

export async function GET() {
  const apiKey = process.env.NEXT_PUBLIC_ASSEMBLYAI_API_KEY ;
  if (!apiKey) {
    return NextResponse.json({ error: "API key not configured" }, { status: 500 });
  }

  const url = new URL("https://streaming.assemblyai.com/v3/token");
  url.searchParams.set("expires_in_seconds", "60"); // valid for 60 seconds

  const response = await fetch(url.toString(), {
    headers: {
      Authorization: apiKey,
    },
  });

  const data = await response.json();
  if (!response.ok) {
    return NextResponse.json({ error: data.error ?? "Failed to generate token" }, { status: response.status });
  }

  return NextResponse.json({ token: data.token });
}
