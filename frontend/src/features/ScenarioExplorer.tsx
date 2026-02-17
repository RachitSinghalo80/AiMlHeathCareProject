import React, { useState } from 'react';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { ExtractedData } from '../types';
import axios from 'axios';
import { RefreshCcw } from 'lucide-react';

interface ScenarioExplorerProps {
    baseData: ExtractedData | null;
}

export const ScenarioExplorer: React.FC<ScenarioExplorerProps> = ({ baseData }) => {
    const [feature, setFeature] = useState<'bmi' | 'blood_glucose_level'>('bmi');
    const [value, setValue] = useState<number>(25);
    const [simulatedRisk, setSimulatedRisk] = useState<number | null>(null);
    const [loading, setLoading] = useState(false);

    // Initialize value from base data when available
    React.useEffect(() => {
        if (baseData) {
            if (feature === 'bmi' && baseData.bmi) setValue(Number(baseData.bmi));
            if (feature === 'blood_glucose_level' && baseData.blood_glucose_level) setValue(Number(baseData.blood_glucose_level));
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

    if (!baseData) return null;

    return (
        <Card className="p-8 mb-16 bg-gradient-to-br from-white to-blue-50 border-2 border-slate-200">
            <div className="flex items-center gap-3 mb-6">
                <div className="bg-tertiary p-2 rounded-lg border-2 border-slate-900 shadow-[4px_4px_0px_0px_rgba(30,41,59,1)]">
                    <RefreshCcw className="text-slate-900" />
                </div>
                <div>
                    <h3 className="text-xl font-bold">What-if Scenario Explorer</h3>
                    <p className="text-muted-foreground text-sm">Simulate how lifestyle changes affect risk.</p>
                </div>
            </div>

            <div className="flex flex-col md:flex-row gap-8 items-end">
                <div className="w-full md:w-1/3">
                    <label className="block text-sm font-bold uppercase mb-2">Adjust Factor</label>
                    <select
                        className="w-full h-12 px-4 rounded-lg border-2 border-slate-300 bg-white font-bold focus:border-accent outline-none"
                        value={feature}
                        onChange={(e) => setFeature(e.target.value as any)}
                    >
                        <option value="bmi">Body Mass Index (BMI)</option>
                        <option value="blood_glucose_level">Blood Glucose (mg/dL)</option>
                    </select>
                </div>

                <div className="w-full md:w-1/3">
                    <label className="block text-sm font-bold uppercase mb-2">
                        Target Value: <span className="text-accent text-lg">{value}</span>
                    </label>
                    <input
                        type="range"
                        min={feature === 'bmi' ? 10 : 50}
                        max={feature === 'bmi' ? 60 : 300}
                        value={value}
                        onChange={(e) => setValue(Number(e.target.value))}
                        className="w-full h-3 bg-slate-200 rounded-full appearance-none accent-accent cursor-pointer"
                    />
                </div>

                <div className="w-full md:w-1/3">
                    <Button onClick={handleSimulate} disabled={loading} className="w-full">
                        {loading ? "Simulating..." : "Run Simulation"}
                    </Button>
                </div>
            </div>

            {simulatedRisk !== null && (
                <div className="mt-8 p-4 bg-white border-2 border-slate-900 rounded-xl shadow-pop text-center animate-popIn">
                    <p className="text-muted-foreground font-bold uppercase text-xs">Projected Risk</p>
                    <p className="text-4xl font-black text-secondary">
                        {(simulatedRisk * 100).toFixed(1)}%
                    </p>
                </div>
            )}
        </Card>
    );
};
