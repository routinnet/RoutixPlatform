import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl
  const token = request.cookies.get('access_token')?.value || 
                request.headers.get('authorization')?.replace('Bearer ', '')

  // Public routes that don't require authentication
  const publicRoutes = ['/login', '/register', '/']
  const isPublicRoute = publicRoutes.includes(pathname)

  // Protected routes
  const protectedRoutes = ['/chat', '/admin', '/profile', '/history']
  const isProtectedRoute = protectedRoutes.some(route => pathname.startsWith(route))

  // Redirect to login if accessing protected route without token
  if (isProtectedRoute && !token) {
    return NextResponse.redirect(new URL('/login', request.url))
  }

  // Redirect to chat if accessing auth pages while logged in
  if (isPublicRoute && token && pathname !== '/') {
    return NextResponse.redirect(new URL('/chat', request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
}