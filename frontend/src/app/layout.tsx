import type { Metadata } from 'next'
import './globals.css'
import { Toaster } from 'react-hot-toast'

export const metadata: Metadata = {
  title: 'LegalCopilot — AI Terms & Conditions Analyzer',
  description: 'Instantly analyze any Terms & Conditions or Privacy Policy. AI-powered risk detection, clause explanation, and user impact analysis.',
  keywords: 'terms and conditions analyzer, privacy policy, legal AI, risk analysis, GDPR',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body>
        {children}
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#ffffff',
              color: '#0f1623',
              border: '1px solid #e2e6ed',
              borderRadius: '10px',
              fontSize: '14px',
              boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
              fontFamily: 'DM Sans, sans-serif',
            },
          }}
        />
      </body>
    </html>
  )
}
