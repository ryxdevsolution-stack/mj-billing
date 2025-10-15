import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { ClientProvider } from '@/contexts/ClientContext'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'RYX Billing Software',
  description: 'Multi-tenant billing system with GST support',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <ClientProvider>
          {children}
        </ClientProvider>
      </body>
    </html>
  )
}
