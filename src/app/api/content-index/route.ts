import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";
import { ContentIndexEntry } from "@/lib/content";

export async function GET() {
  try {
    const indexPath = path.join(process.cwd(), "data", "content_index.json");

    if (!fs.existsSync(indexPath)) {
      return NextResponse.json([], { status: 200 });
    }

    const data = fs.readFileSync(indexPath, "utf-8");
    const content = JSON.parse(data) as ContentIndexEntry[];

    // Sort by timestamp (descending) before returning
    const sortedContent = content.sort((a: ContentIndexEntry, b: ContentIndexEntry) => (b.timestamp || 0) - (a.timestamp || 0));

    console.log("API /api/content-index - Top 5 items:");
    sortedContent.slice(0, 5).forEach((item: ContentIndexEntry, i: number) => {
      console.log(`${i+1}. ${item.title} - timestamp: ${item.timestamp}`);
    });

    return NextResponse.json(sortedContent, { status: 200 });
  } catch (error) {
    console.error("Error reading content index:", error);
    return NextResponse.json([], { status: 200 });
  }
}
