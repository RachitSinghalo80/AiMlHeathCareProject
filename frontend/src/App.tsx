import React, { useState } from 'react';
import { Layout } from './components/layout';
import { UploadSection } from './features/UploadSection';
import { PatientDashboard } from './features/PatientDashboard';
import { ScenarioExplorer } from './features/ScenarioExplorer';
import { DrugInfoSection } from './features/DrugInfoSection';
import type { ExtractedData, RiskAnalysis } from './types';

function App() {
  const [extractedData, setExtractedData] = useState<ExtractedData | null>(null);
  const [riskAnalysis, setRiskAnalysis] = useState<RiskAnalysis | null>(null);

  const handleDataExtracted = (data: ExtractedData, filename: string) => {
    setExtractedData(data);
    setRiskAnalysis(null);

    // Scroll to dashboard
    setTimeout(() => {
      document.getElementById('dashboard')?.scrollIntoView();
    }, 100);
  };

  const handleRiskCalculated = (analysis: RiskAnalysis) => {
    setRiskAnalysis(analysis);
  };

  return (
    <Layout>
      <div className="space-y-16">

        {/* Main Navigation / Action Choice */}
        {!extractedData && (
          <div className="grid md:grid-cols-2 gap-6">
            <div onClick={() => document.getElementById('upload')?.scrollIntoView()} className="cursor-pointer group">
              <div className="bg-blue-50/50 p-8 rounded-2xl border-2 border-blue-200 hover:border-blue-400 hover:bg-blue-100/50 transition-all text-center h-full flex flex-col items-center justify-center gap-4">
                <span className="text-4xl group-hover:scale-110 transition-transform duration-300">📄</span>
                <div>
                  <h3 className="text-xl font-bold text-slate-800 mb-1">Analyze Report</h3>
                  <p className="text-sm text-slate-600">Upload PDF to estimate risk</p>
                </div>
              </div>
            </div>
            <div onClick={() => document.getElementById('drugs')?.scrollIntoView()} className="cursor-pointer group">
              <div className="bg-purple-50/50 p-8 rounded-2xl border-2 border-purple-200 hover:border-purple-400 hover:bg-purple-100/50 transition-all text-center h-full flex flex-col items-center justify-center gap-4">
                <span className="text-4xl group-hover:scale-110 transition-transform duration-300">💊</span>
                <div>
                  <h3 className="text-xl font-bold text-slate-800 mb-1">Drug Lookup</h3>
                  <p className="text-sm text-slate-600">Search medication info</p>
                </div>
              </div>
            </div>
          </div>
        )}

        <UploadSection onDataExtracted={handleDataExtracted} />

        {extractedData && (
          <div id="dashboard" className="animate-fadeIn">
            <PatientDashboard
              data={extractedData}
              onRiskCalculated={handleRiskCalculated}
              riskAnalysis={riskAnalysis}
            />

            {riskAnalysis && (
              <div className="mt-12">
                <ScenarioExplorer baseData={extractedData} />
              </div>
            )}
          </div>
        )}

        <div id="drugs" className="pt-12 border-t-2 border-slate-100">
          <DrugInfoSection
            riskAnalysis={riskAnalysis}
            extractedData={extractedData}
          />
        </div>

      </div>
    </Layout>
  );
}

export default App;
