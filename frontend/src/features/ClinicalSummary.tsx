import React, { useState } from 'react';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { FileText, User, Stethoscope, Sparkles } from 'lucide-react';
import type { RiskAnalysis, ExtractedData } from '../types';
import axios from 'axios';

interface ClinicalSummaryProps {
    riskAnalysis: RiskAnalysis;
    data: ExtractedData;
}

export const ClinicalSummary: React.FC<ClinicalSummaryProps> = ({ riskAnalysis, data }) => {
    const [mode, setMode] = useState<'patient' | 'doctor'>('patient');
    const [summaries, setSummaries] = useState<{ patient: string | null; doctor: string | null }>({
        patient: null,
        doctor: null
    });
    const [loading, setLoading] = useState(false);

    const fetchSummary = async () => {
        setLoading(true);
        try {
            const res = await axios.post('/api/clinical-summary', {
                risk_score: riskAnalysis.risk_score,
                shap_features: riskAnalysis.shap_values,
                data: data,
                mode: mode
            });
            setSummaries(prev => ({ ...prev, [mode]: res.data.summary }));
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    // Simple markdown formatter for bold text
    const formatText = (text: string) => {
        return text.split('\n').map((line, i) => (
            <React.Fragment key={i}>
                {line.split(/(\*\*.*?\*\*)/).map((part, j) =>
                    part.startsWith('**') && part.endsWith('**') ? (
                        <strong key={j} className="font-bold text-slate-900">{part.slice(2, -2)}</strong>
                    ) : (
                        part
                    )
                )}
                <br />
            </React.Fragment>
        ));
    };

    const currentSummary = summaries[mode];

    return (
        <Card className="p-6 mt-8 relative overflow-hidden bg-slate-50 border-2 border-slate-200">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 gap-4">
                <div>
                    <h3 className="text-xl font-bold flex items-center gap-2">
                        <FileText className="text-accent" /> Clinical Summary
                    </h3>
                    <p className="text-sm text-muted-foreground">AI-generated health report.</p>
                </div>

                <div className="flex bg-slate-200 p-1 rounded-lg">
                    <button
                        onClick={() => setMode('patient')}
                        className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-bold transition-all ${mode === 'patient' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-700'}`}
                    >
                        <User size={16} /> Patient View
                    </button>
                    <button
                        onClick={() => setMode('doctor')}
                        className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-bold transition-all ${mode === 'doctor' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-700'}`}
                    >
                        <Stethoscope size={16} /> Doctor View
                    </button>
                </div>
            </div>

            <div className="bg-white p-6 rounded-xl border border-slate-200 min-h-[150px] relative">
                {currentSummary ? (
                    <div className="prose prose-slate max-w-none text-slate-700 leading-relaxed">
                        {formatText(currentSummary)}
                    </div>
                ) : (
                    <div className="absolute inset-0 flex flex-col items-center justify-center text-center p-6 bg-slate-50/50">
                        <p className="text-slate-500 mb-4 max-w-md">
                            Generate a customized summary explaining the risk factors and health implications in {mode === 'patient' ? 'simple language' : 'medical terminology'}.
                        </p>
                        <Button
                            onClick={fetchSummary}
                            disabled={loading}
                            className="shadow-lg shadow-accent/20 transition-all hover:scale-105"
                        >
                            <Sparkles size={16} className="mr-2" />
                            {loading ? "Generating Insight..." : "Generate Summary"}
                        </Button>
                    </div>
                )}

                {loading && !currentSummary && (
                    <div className="absolute inset-0 bg-white/80 backdrop-blur-sm flex items-center justify-center z-10">
                        <div className="flex flex-col items-center gap-3">
                            <div className="flex gap-2">
                                <div className="w-3 h-3 bg-accent rounded-full animate-bounce" style={{ animationDelay: '0s' }} />
                                <div className="w-3 h-3 bg-accent rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                                <div className="w-3 h-3 bg-accent rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                            </div>
                            <span className="text-sm font-bold text-accent">Analyzing Data...</span>
                        </div>
                    </div>
                )}
            </div>

            {currentSummary && (
                <div className="mt-4 flex justify-end gap-2">
                    <Button variant="outline" size="sm" onClick={fetchSummary} disabled={loading}>
                        Regenerate
                    </Button>
                    <Button variant="secondary" size="sm" onClick={() => window.print()}>
                        Download / Print Report
                    </Button>
                </div>
            )}
        </Card>
    );
};
