import { NextRequest, NextResponse } from 'next/server'

// Edge Runtime：build 时会注入环境变量
// fallback 到 hardcode 确保 Edge 环境一定能读到
const USERNAME = process.env.BASIC_AUTH_USER ?? 'rtc2026'
const PASSWORD = process.env.BASIC_AUTH_PASS ?? 'rtc2026'

function unauthorized() {
  return new NextResponse('Unauthorized', {
    status: 401,
    headers: { 'WWW-Authenticate': 'Basic realm="GEO Ops Panel"' },
  })
}

export function middleware(req: NextRequest) {
  // webhook 接口跳过认证（Skill 脚本直接调用）
  if (req.nextUrl.pathname.startsWith('/api/webhook')) {
    return NextResponse.next()
  }

  const authHeader = req.headers.get('authorization') ?? ''
  if (!authHeader.startsWith('Basic ')) return unauthorized()

  let user: string, pass: string
  try {
    const decoded = atob(authHeader.slice(6))
    const colon   = decoded.indexOf(':')
    if (colon === -1) return unauthorized()
    user = decoded.slice(0, colon)
    pass = decoded.slice(colon + 1)
  } catch {
    return unauthorized()
  }

  // 固定账号密码兜底（Edge Runtime 环境变量偶发读不到时保证可用）
  const validUser = USERNAME || 'rtc2026'
  const validPass = PASSWORD || 'rtc2026'

  if (user === validUser && pass === validPass) {
    return NextResponse.next()
  }
  return unauthorized()
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
}
