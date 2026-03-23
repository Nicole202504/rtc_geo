import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'GEO 内容运营平台',
  description: 'TRTC GEO 内容生产管理面板',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body className={inter.className}>
        <div className="min-h-screen bg-gray-50">
          {/* 顶部导航 */}
          <nav className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-7 h-7 bg-blue-600 rounded-md flex items-center justify-center">
                <span className="text-white text-xs font-bold">G</span>
              </div>
              <span className="font-semibold text-gray-900">GEO 内容运营平台</span>
            </div>
            <div className="flex items-center gap-6 text-sm text-gray-600">
              <a href="/" className="hover:text-gray-900">Campaigns</a>
              <a href="/review" className="hover:text-gray-900">审核台</a>
              <a href="/api/health" className="hover:text-gray-900 text-xs text-gray-400">API</a>
            </div>
          </nav>
          <main>{children}</main>
        </div>
      </body>
    </html>
  )
}
