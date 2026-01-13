import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";
import { updateSession } from "./lib/auth/middleware";

export async function middleware(request: NextRequest) {
  const response = await updateSession(request);
  const pathname = request.nextUrl.pathname;
  if (
    pathname.startsWith("/welcome") ||
    pathname.startsWith("/onboarding") ||
    pathname.startsWith("/setup") ||
    pathname.startsWith("/api")
  ) {
    return response;
  }
  const apiBase = process.env.OAP_API_URL ?? "http://localhost:8000";
  const apiToken = process.env.OAP_API_TOKEN;
  try {
    const profileResponse = await fetch(`${apiBase}/api/org/profile`, {
      headers: apiToken ? { "X-API-Key": apiToken } : {},
      cache: "no-store",
    });
    if (profileResponse.ok) {
      const data = (await profileResponse.json()) as {
        onboarding_stage?: number;
      };
      if ((data.onboarding_stage ?? 0) < 1) {
        const url = request.nextUrl.clone();
        url.pathname = "/welcome";
        return NextResponse.redirect(url);
      }
    }
  } catch (_error) {
    return response;
  }
  return response;
}

export const config = {
  // Skip middleware for static assets and endpoints that handle auth
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - api/auth (auth API routes)
     */
    "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",

    /*
     * Match all API routes except for auth-related ones
     * This allows the middleware to run on API routes and check authentication
     */
    "/api/((?!auth).*)",
  ],
};
