import { createBrowserClient } from "@supabase/ssr"

// TVS Mitra Chatbot Database (cqgclaolwohxxvlpscee)
const SUPABASE_URL = "https://cqgclaolwohxxvlpscee.supabase.co"
const SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNxZ2NsYW9sd29oeHh2bHBzY2VlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzMyMTQ2NzgsImV4cCI6MjA4ODc5MDY3OH0.X2w8g90HRdKlSO3bEvSvrNN5mxyJ_1SrsgQV2Fa5zdk"

export function createClient() {
  return createBrowserClient(SUPABASE_URL, SUPABASE_ANON_KEY)
}
