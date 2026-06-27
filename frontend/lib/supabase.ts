import { createClient, SupabaseClient } from "@supabase/supabase-js";

let client: SupabaseClient | null = null;

export async function getSupabaseClient(): Promise<SupabaseClient | null> {
  if (client) return client;

  try {
    const res = await fetch("http://localhost:8000/api/v1/users/config");
    if (!res.ok) return null;
    const json = await res.json();
    const { supabase_url, supabase_anon_key } = json.data;
    if (!supabase_url || !supabase_anon_key) return null;
    client = createClient(supabase_url, supabase_anon_key);
    return client;
  } catch {
    return null;
  }
}
