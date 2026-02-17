import React, { useState } from 'react';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import type { ExtractedData } from '../types';
import axios from 'axios';
import { RefreshCcw } from 'lucide-react';

interface ScenarioExplorerProps {
    baseData: ExtractedData | null;
}

export const ScenarioExplorer: React.FC<ScenarioExplorerProps> = ({ baseData }) => {
    const [feature, setFeature] = useState<'bmi' | 'blood_glucose_level' | 'HbA1c_level' | 'age'>('bmi');
    const [value, setValue] = useState<number>(25);
    const [simulatedRisk, setSimulatedRisk] = useState<number | null>(null);
    const [loading, setLoading] = useState(false);

    // Initialize value from base data when available
    React.useEffect(() => {
        if (baseData) {
            if (feature === 'bmi' && baseData.bmi) setValue(Number(baseData.bmi));
            if (feature === 'blood_glucose_level' && baseData.blood_glucose_level) setValue(Number(baseData.blood_glucose_level));
            if (feature === 'HbA1c_level' && baseData.HbA1c_level) setValue(Number(baseData.HbA1c_level));
            if (feature === 'age' && baseData.age) setValue(Number(baseData.age));
        }
    }, [baseData, feature]);

    const handleSimulate = async () => {
        if (!baseData) return;
        setLoading(true);
        try {
            const res = await axios.post('/api/simulate', {
                base_data: baseData,
                feature,
                value
            });
            setSimulatedRisk(res.data.simulated_risk);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Card className="p-8 mb-16 bg-white border-2 border-slate-200 shadow-xl relative overflow-hidden">

            <div className="flex items-center gap-3 mb-6 relative z-10">
                <div className="bg-tertiary text-white p-2 rounded-lg shadow-md rotate-[-3deg]">
                    <RefreshCcw size={24} />
                </div>
                <div>
                    <h3 className="text-xl font-bold">What-if Scenario Explorer</h3>
                    <p className="text-muted-foreground text-sm font-medium">Simulate how lifestyle changes affect risk.</p>
                </div>
            </div>

            <div className="flex flex-col md:flex-row gap-8 items-end relative z-10">
                <div className="w-full md:w-1/3">
                    <label className="block text-sm font-bold uppercase mb-2 text-slate-500">Adjust Factor</label>
                    <div className="relative">
                        <select
                            className="w-full h-12 px-4 rounded-xl border-2 border-slate-200 bg-slate-50 font-bold focus:border-accent outline-none appearance-none"
                            value={feature}
                            onChange={(e) => setFeature(e.target.value as any)}
                        >
                            <option value="bmi">Body Mass Index (BMI)</option>
                            <option value="blood_glucose_level">Blood Glucose (mg/dL)</option>
                            <option value="HbA1c_level">HbA1c Level</option>
                            <option value="age">Age (Years)</option>
                        </select>
                        <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-slate-400">▼</div>
                    </div>
                </div>

                <div className="w-full md:w-1/3">
                    <label className="block text-sm font-bold uppercase mb-2 text-slate-500">
                        Target Value: <span className="text-accent text-lg ml-1">{value}</span>
                    </label>
                    <div className="h-12 flex items-center bg-slate-50 rounded-xl px-4 border-2 border-slate-200">
                        <input
                            type="range"
                            min={feature === 'bmi' ? 10 : feature === 'HbA1c_level' ? 3 : feature === 'age' ? 18 : 50}
                            max={feature === 'bmi' ? 60 : feature === 'HbA1c_level' ? 15 : feature === 'age' ? 100 : 300}
                            step={feature === 'HbA1c_level' ? 0.1 : 1}
                            value={value}
                            onChange={(e) => setValue(Number(e.target.value))}
                            className="w-full h-2 bg-slate-200 rounded-full appearance-none accent-tertiary cursor-pointer hover:accent-accent"
                        />
                    </div>
                </div>

                <div className="w-full md:w-1/3">
                    <Button onClick={handleSimulate} disabled={loading} className="w-full h-12 shadow-md">
                        {loading ? "Simulating..." : "Run Simulation"}
                    </Button>
                </div>
            </div>

            {simulatedRisk !== null && (
                <div className="mt-8 p-6 bg-slate-50 border-2 border-slate-200 rounded-xl text-center animate-popIn">
                    <div className="flex flex-col md:flex-row items-center justify-center gap-8">
                        <div className="text-right">
                            <p className="text-muted-foreground font-bold uppercase text-xs tracking-widest mb-1">Current Risk</p>
                            <p className="text-xl font-bold text-slate-400">
                                {baseData && baseData.risk_score ? (Number(baseData.risk_score) * 100).toFixed(1) : '-'}%
                            </p>
                        </div>

                        <div className="h-8 w-px bg-slate-300 hidden md:block"></div>

                        <div className="text-left">
                            <p className="text-accent font-bold uppercase text-xs tracking-widest mb-1">Projected Risk</p>
                            <p className="text-4xl font-black text-secondary leading-none">
                                {(simulatedRisk * 100).toFixed(1)}%
                            </p>
                        </div>
                    </div>
                </div>
            )}
        </Card>
    );
};
