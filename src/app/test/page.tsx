import VastAd from "@/components/VastAd";
import { Metadata } from "next";

export async function generateMetadata(): Promise<Metadata> {
  return {
    title: "Test Page - VAST Ad",
    description: "Test page for VAST ad",
  };
}

export default function TestPage() {
  return (
    <div className="bg-background text-foreground min-h-screen" style={{ padding: "20px" }}>
      <h1 style={{ textAlign: "center", marginBottom: "20px" }}>Test Page - VAST Ad</h1>
      <p style={{ textAlign: "center", marginBottom: "20px" }}>This page tests the VAST ad with zoneid 5980970</p>
      
      <VastAd />
      
      <div style={{ marginTop: "40px", textAlign: "center" }}>
        <a href="/" style={{ color: "#3b82f6", textDecoration: "underline" }}>Back to Home</a>
      </div>
    </div>
  );
}
