/**
 * Landing Page
 * 
 * Redirects to the dashboard.
 */

import { redirect } from "next/navigation";

export default function Home() {
  redirect("/dashboard");
}
