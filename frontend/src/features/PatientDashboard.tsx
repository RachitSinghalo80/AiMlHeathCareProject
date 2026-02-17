import React, { useEffect } from 'react';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import type { ExtractedData, RiskAnalysis } from '../types';
import axios from 'axios';
import { motion } from 'framer-motion';
import { AlertTriangle, CheckCircle, TrendingUp, TrendingDown, Activity } from 'lucide-react';
import { ClinicalSummary } from './ClinicalSummary';

interface PatientDashboardProps {
    data: ExtractedData;
    onRiskCalculated: (analysis: RiskAnalysis) => void;
    riskAnalysis: RiskAnalysis | null;
}

export const PatientDashboard: React.FC<PatientDashboardProps> = ({ data, onRiskCalculated, riskAnalysis }) => {
    const [loading, setLoading] = React.useState(false);
    const [confirmed, setConfirmed] = React.useState(false);

    const calculateRisk = async () => {
        setLoading(true);
        try {
            const res = await axios.post('/api/predict', { data });
            onRiskCalculated(res.data);
        } catch (err: any) {
            console.error(err);
            const msg = err.response?.data?.error || "Failed to calculate risk";
            alert(`Error: ${msg}`);
        } finally {
            setLoading(false);
        }
    };

    const getRiskColor = (level: string) => {
        switch (level) {
            case 'LOW': return 'text-quaternary';
            case 'MEDIUM': return 'text-tertiary';
            case 'HIGH': return 'text-secondary'; // pink/red
            default: return 'text-foreground';
        }
    };

    const getBarColor = (val: number) => val > 0 ? 'bg-secondary' : 'bg-quaternary';

    return (
        <section id="dashboard" className="mb-16">

            <div className="grid md:grid-cols-2 gap-8 mb-8">
                {/* Patient Data Card */}
                <Card className="p-6 relative overflow-hidden">
                    <div className="absolute top-0 right-0 p-4 opacity-10">
                        <Activity size={120} />
                    </div>
                    <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                        <span className="bg-blue-100 p-2 rounded-full">👤</span> Patient Snapshot
                    </h3>

                    <div className="space-y-3 relative z-10">
                        {Object.entries(data).map(([key, value]) => {
                            if (value === null) return null;
                            return (
                                <div key={key} className="flex justify-between border-b border-slate-100 pb-2">
                                    <span className="font-medium capitalize text-muted-foreground">{key.replace(/_/g, ' ')}</span>
                                    <span className="font-bold">{String(value)}</span>
                                </div>
                            );
                        })}
                    </div>

                    {!riskAnalysis && (
                        <div className="mt-6">
                            <label className="flex items-center gap-3 cursor-pointer bg-slate-50 p-3 rounded-lg border border-slate-200 hover:bg-slate-100 transition-colors">
                                <input type="checkbox" className="w-5 h-5 accent-accent" checked={confirmed} onChange={(e) => setConfirmed(e.target.checked)} />
                                <span className="font-bold text-sm">I confirm these values are correct</span>
                            </label>

                            <Button
                                className="w-full mt-4"
                                disabled={!confirmed || loading}
                                onClick={calculateRisk}
                            >
                                {loading ? "Analyzing..." : "Assess Clinical Risk"}
                            </Button>
                        </div>
                    )}
                </Card>

                {/* Risk Result Card */}
                <AnimatePresence mode='wait'>
                    {riskAnalysis && (
                        <motion.div
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                        >
                            <Card variant="featured" className="p-6 h-full flex flex-col justify-center items-center text-center relative overflow-hidden border-4 border-slate-900">
                                <div className="absolute inset-0 bg-dot-pattern opacity-10 pointer-events-none" />

                                <h3 className="text-lg font-bold uppercase tracking-widest text-muted-foreground mb-2">Estimated Risk</h3>

                                <div className={`text-6xl font-black mb-2 ${getRiskColor(riskAnalysis.risk_level)}`}>
                                    {riskAnalysis.risk_level}
                                </div>

                                <div className="text-4xl font-bold mb-6">
                                    {(riskAnalysis.risk_score * 100).toFixed(1)}%
                                </div>

                                <div className="w-full bg-slate-200 h-4 rounded-full overflow-hidden border-2 border-slate-900 mb-6">
                                    <motion.div
                                        initial={{ width: 0 }}
                                        animate={{ width: `${Math.min(riskAnalysis.risk_score * 100, 100)}%` }}
                                        className={`h-full ${riskAnalysis.risk_level === 'HIGH' ? 'bg-secondary' : riskAnalysis.risk_level === 'MEDIUM' ? 'bg-tertiary' : 'bg-quaternary'}`}
                                    />
                                </div>

                                <div className="flex gap-2 text-sm font-bold bg-white/50 p-2 rounded-lg backdrop-blur-sm">
                                    {riskAnalysis.risk_level === 'HIGH' ? <AlertTriangle className="text-secondary" /> : <CheckCircle className="text-quaternary" />}
                                    <span>
                                        {riskAnalysis.risk_level === 'HIGH' ? 'Elevated Risk Detected' : 'Risk levels appear normal'}
                                    </span>
                                </div>
                            </Card>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>

            {/* SHAP Analysis */}
            {riskAnalysis && (
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                >
                    <h3 className="text-2xl font-bold mb-6 flex items-center gap-2">
                        <TrendingUp className="text-accent" /> Key Risk Drivers
                    </h3>

                    <div className="grid md:grid-cols-2 gap-8">
                        <Card className="p-6">
                            <h4 className="font-bold mb-4">Top Influencing Factors</h4>
                            <div className="space-y-4">
                                {riskAnalysis.top_factors.map(([feature, value], idx) => (
                                    <div key={idx} className="relative">
                                        <div className="flex justify-between text-sm font-bold mb-1">
                                            <span className="capitalize">{feature.replace(/_/g, ' ')}</span>
                                            <span className={value > 0 ? "text-secondary" : "text-quaternary"}>
                                                {value > 0 ? "Increases Risk" : "Reduces Risk"}
                                            </span>
                                        </div>
                                        <div className="w-full bg-slate-100 h-3 rounded-full overflow-hidden shadow-inner">
                                            <div
                                                className={`h-full rounded-full shadow-sm transition-all duration-500 ${value > 0 ? 'bg-gradient-to-r from-red-400 to-red-500' : 'bg-gradient-to-r from-emerald-400 to-emerald-500'}`}
                                                style={{ width: `${Math.min(Math.abs(value) * 100, 100)}%` }} // scaling for visuals
                                            />
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </Card>

                        <Card className="p-6 bg-slate-50 border-dashed">
                            <h4 className="font-bold mb-4">Grouped Analysis</h4>
                            <div className="space-y-4">
                                {Object.entries(riskAnalysis.grouped_features).map(([group, items]) => (
                                    items.length > 0 && (
                                        <div key={group}>
                                            <h5 className="font-bold text-sm text-muted-foreground uppercase mb-2">{group}</h5>
                                            <ul className="space-y-1">
                                                {items.map(([name, val], i) => (
                                                    <li key={i} className="flex items-center gap-2 text-sm">
                                                        {val > 0 ? <TrendingUp size={14} className="text-secondary" /> : <TrendingDown size={14} className="text-quaternary" />}
                                                        <span className="capitalize">{name.replace(/_/g, ' ')}</span>
                                                    </li>
                                                ))}
                                            </ul>
                                        </div>
                                    )
                                ))}
                            </div>
                        </Card>
                    </div>

                    <ClinicalSummary riskAnalysis={riskAnalysis} data={data} />
                </motion.div>
            )}
        </section>
    );
};

import { AnimatePresence } from 'framer-motion';
