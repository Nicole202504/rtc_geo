import { NextRequest, NextResponse } from 'next/server'

const USERNAME = process.env.BASIC_AUTH_USER || 'rtc2026'
const PASSWORD = process.env.BASIC_AUTH_PASS || 'rtc2026'

export function middleware(req: NextRequest) {
  // webhook 接口不需要登录（Skill 脚本直接调用）
  if (req.nextUrl.pathname.startsWith('/api/webhook')) {
    return NextResponse.next()
  }

  const authHeader = req.headers.get('authorization')

  if (authHeader && authHeader.startsWith('Basic ')) {
    const base64 = authHeader.slice(6)          // 去掉 "Basic "
    const decoded = atob(base64)                 // Edge Runtime 支持 atob
    const colon = decoded.indexOf(':')
    const user = decoded.slice(0, colon)
    const pass = decoded.slice(colon + 1)
    if (user === USERNAME && pass === PASSWORD) {
      return NextResponse.next()
    }
  }

  // 未登录 → 返回 401，浏览器弹出登录框
  return new NextResponse('Unauthorized', {
    status: 401,
    headers: {
      'WWW-Authenticate': 'Basic realm="GEO Ops Panel"',
    },
  })
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
}
