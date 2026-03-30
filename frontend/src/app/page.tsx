'use client'

import { useState } from 'react'
import { AnalyzeResponse } from '@/types'
import Header from '@/components/Header'
import UploadSection from '@/components/upload/UploadSection'
import Dashboard from '@/components/dashboard/Dashboard'
import CompareView from '@/components/comparison/CompareView'

type View = 'home' | 'results' | 'compare'

export default function HomePage() {
  const [view, setView] = useState<View>('home')
  const [analysisResult, setAnalysisResult] = useState<AnalyzeResponse | null>(null)
  const [documentText, setDocumentText] = useState<string>('')

  const handleAnalysisComplete = (result: AnalyzeResponse, text: string) => {
    setAnalysisResult(result)
    setDocumentText(text)
    setView('results')
  }

  const handleReset = () => {
    setView('home')
    setAnalysisResult(null)
    setDocumentText('')
  }

  return (
    <div style={{ minHeight: '100vh', backgroundColor: 'var(--bg-base)' }}>
      <Header
        onHome={handleReset}
        onCompare={() => setView('compare')}
        currentView={view}
      />

      <main>
        {view === 'home' && (
          <UploadSection onAnalysisComplete={handleAnalysisComplete} />
        )}

        {view === 'results' && analysisResult && (
          <Dashboard
            result={analysisResult}
            documentText={documentText}
            onReset={handleReset}
          />
        )}

        {view === 'compare' && (
          <CompareView onBack={() => setView('home')} />
        )}
      </main>
    </div>
  )
}
