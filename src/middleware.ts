import { NextRequest, NextResponse } from 'next/server'

const USERNAME = process.env.BASIC_AUTH_USER || 'rtc2026'
const PASSWORD = process.env.BASIC_AUTH_PASS || 'rtc2026'

export function middleware(req: NextRequest) {
  // webhook 接口不需要登录（Skill 脚本直接调用）
  if (req.nextUrl.pathname.startsWith('/api/webhook')) {
    return NextResponse.next()
  }

  const authHeader = req.headers.get('authorization')

  if (authHeader) {
    const base64 = authHeader.replace('Basic ', '')
    const decoded = Buffer.from(base64, 'base64').toString('utf-8')
    const [user, pass] = decoded.split(':')
    if (user === USERNAME && pass === PASSWORD) {
      return NextResponse.next()
    }
  }

  // 未登录 → 返回 401，触发浏览器弹出登录框
  return new NextResponse('Unauthorized', {
    status: 401,
    headers: {
      'WWW-Authenticate': 'Basic realm="GEO Ops Panel"',
    },
  })
}

export const config = {
  // 匹配所有路径（除静态资源外）
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
}
