import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export const STATUS_LABELS: Record<string, string> = {
  draft: '草稿',
  analyzing: '分析中',
  writing: '写作中',
  reviewing: '审核中',
  publishing: '发布中',
  completed: '已完成',
  paused: '已暂停',
  pending: '待处理',
  generating: '生成中',
  approved: '已通过',
  rejected: '已拒绝',
  published: '已发布',
}

export const STATUS_COLORS: Record<string, string> = {
  draft: 'bg-gray-100 text-gray-700',
  analyzing: 'bg-blue-100 text-blue-700',
  writing: 'bg-purple-100 text-purple-700',
  reviewing: 'bg-yellow-100 text-yellow-700',
  publishing: 'bg-orange-100 text-orange-700',
  completed: 'bg-green-100 text-green-700',
  paused: 'bg-gray-100 text-gray-500',
  pending: 'bg-gray-100 text-gray-600',
  generating: 'bg-purple-100 text-purple-700',
  approved: 'bg-green-100 text-green-700',
  rejected: 'bg-red-100 text-red-700',
  published: 'bg-green-100 text-green-800',
}
