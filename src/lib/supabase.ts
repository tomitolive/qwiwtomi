import { createClient } from "@supabase/supabase-js";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY!;

/**
 * Supabase client for server-side data fetching (no auth/cookies needed).
 * Used in Server Components and generateMetadata.
 */
export function getDataClient() {
  return createClient(supabaseUrl, supabaseKey);
}
