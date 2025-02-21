import React, { useState, useEffect } from 'react'
import { useKnowledgeBase } from '../context/KnowledgeBaseContext'
import GoogleDriveIntegration from '../components/GoogleDriveIntegration'
import FileUpload from '../components/FileUpload'
import SupabaseTableSelector from '../components/SupabaseTableSelector'
import VectorizationTrigger from '../components/VectorizationTrigger'
import './KnowledgeBase.css'

export default function KnowledgeBase() {
  const { state, actions } = useKnowledgeBase()
  const [currentStep, setCurrentStep] = useState(1)

  useEffect(() => {
    actions.loadFiles()
    actions.loadTables()
  }, [actions])

  const steps = [
    {
      number: 1,
      label: 'Document Selection',
      component: (
        <div className="document-sources">
          <div className="google-drive-section">
            <h3>Select from Google Drive</h3>
            <GoogleDriveIntegration 
              files={state.files}
              selectedFiles={state.selectedFiles}
              onFileSelect={(file) => actions.selectFile(file)}
              onFileRemove={(fileId) => actions.removeFile(fileId)}
            />
          </div>
          <div className="upload-section">
            <h3>Upload Documents</h3>
            <FileUpload onFileUpload={(file) => actions.selectFile(file)} />
            <div className="selected-files">
              <h4>Selected Files:</h4>
              <ul>
                {state.selectedFiles.map((file) => (
                  <li key={file.id}>
                    {file.name}
                    <button onClick={() => actions.removeFile(file.id)}>
                      Remove
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )
    },
    {
      number: 2,
      label: 'Supabase Integration',
      component: (
        <div className="supabase-section">
          <SupabaseTableSelector 
            tables={state.supabaseTables}
            selectedTable={state.selectedTable}
            onSelect={(table) => actions.selectTable(table)}
          />
        </div>
      )
    },
    {
      number: 3,
      label: 'Vectorization',
      component: (
        <div className="vectorization-section">
          <VectorizationTrigger 
            files={state.selectedFiles}
            supabaseTable={state.selectedTable}
            isVectorizing={state.isLoading}
            onVectorize={() => {
              if (state.selectedFiles.length > 0 && state.selectedTable) {
                actions.vectorizeDocuments(state.selectedFiles, state.selectedTable)
              }
            }}
          />
        </div>
      )
    }
  ]

  const nextStep = () => {
    setCurrentStep(prev => Math.min(prev + 1, steps.length))
  }

  const prevStep = () => {
    setCurrentStep(prev => Math.max(prev - 1, 1))
  }

  return (
    <div className="knowledge-base-page">
      <h1>Knowledge Base Configuration</h1>

      {state.error && (
        <div className="error-banner">
          <p>{state.error}</p>
        </div>
      )}

      <div className="workflow-container">
        <div className="workflow-steps">
          {steps.map((step) => (
            <div 
              key={step.number}
              className={`workflow-step ${
                step.number === currentStep ? 'active' : ''
              } ${step.number < currentStep ? 'completed' : ''}`}
            >
              <div className="step-number">{step.number}</div>
              <div className="step-label">{step.label}</div>
            </div>
          ))}
        </div>

        <div className="step-container">
          {steps.map((step) => (
            <div 
              key={step.number}
              className={`step ${
                step.number === currentStep ? 'active' : ''
              } ${step.number < currentStep ? 'previous' : ''}`}
            >
              {step.component}
            </div>
          ))}
        </div>
      </div>

      <div className="navigation-buttons">
        {currentStep > 1 && (
          <button className="prev-button" onClick={prevStep}>
            ← Previous
          </button>
        )}
        {currentStep < steps.length && (
          <button className="next-button" onClick={nextStep}>
            Next →
          </button>
        )}
      </div>
    </div>
  )
}
