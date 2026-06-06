import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

export async function GET() {
  try {
    const indexPath = path.join(process.cwd(), "data", "content_index.json");
    
    if (!fs.existsSync(indexPath)) {
      return NextResponse.json([], { status: 200 });
    }

    const data = fs.readFileSync(indexPath, "utf-8");
    const content = JSON.parse(data);
    
    return NextResponse.json(content, { status: 200 });
  } catch (error) {
    console.error("Error reading content index:", error);
    return NextResponse.json([], { status: 200 });
  }
}
