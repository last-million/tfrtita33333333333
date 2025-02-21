import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { ThemeProvider } from './context/ThemeContext'
import { LanguageProvider } from './context/LanguageContext'
import { KnowledgeBaseProvider } from './context/KnowledgeBaseContext'
import Header from './components/Header'
import Dashboard from './pages/Dashboard'
import Authentication from './pages/Authentication'
import CallHistory, { CallDetail } from './pages/CallHistory'
import KnowledgeBase from './pages/KnowledgeBase'
import CallManager from './pages/CallManager'
import SystemConfig from './pages/SystemConfig'
import './App.css'

function App() {
  return (
    <ThemeProvider>
      <LanguageProvider>
        <KnowledgeBaseProvider>
          <Router>
            <div className="app-container">
              <Header />
              <main className="main-content">
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/auth" element={<Authentication />} />
                  <Route path="/calls" element={<CallManager />} />
                  <Route path="/call-history" element={<CallHistory />} />
                  <Route path="/call-history/:callSid" element={<CallDetail />} />
                  <Route path="/knowledge-base" element={<KnowledgeBase />} />
                  <Route path="/system-config" element={<SystemConfig />} />
                </Routes>
              </main>
            </div>
          </Router>
        </KnowledgeBaseProvider>
      </LanguageProvider>
    </ThemeProvider>
  )
}

export default App
