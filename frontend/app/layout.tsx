import './styles/globals.css'
import { ReactNode } from 'react'
import Providers from './providers'

export const metadata = {
  title: 'SPARK AI Platform',
  description: 'AI Platform for Chronosphere'
}

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}
