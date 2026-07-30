import NewAd from "@/components/NewAd";
import { Metadata } from "next";

export async function generateMetadata(): Promise<Metadata> {
  return {
    title: "Test Page - New Ad",
    description: "Test page for new ad",
  };
}

export default function TestPage() {
  return (
    <div className="bg-background text-foreground min-h-screen" style={{ padding: "20px" }}>
      <h1 style={{ textAlign: "center", marginBottom: "20px" }}>Test Page - New Ad</h1>
      <p style={{ textAlign: "center", marginBottom: "20px" }}>This page tests the new ad script</p>
      
      <NewAd />
      
      <div style={{ marginTop: "40px", textAlign: "center" }}>
        <a href="/" style={{ color: "#3b82f6", textDecoration: "underline" }}>Back to Home</a>
      </div>
    </div>
  );
}
