import React, { useState } from 'react';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import type { DrugInfoResult, DrugRecommendation, RiskAnalysis, ExtractedData } from '../types';
import axios from 'axios';
import { Pill, Search, Info } from 'lucide-react';

interface DrugInfoSectionProps {
    riskAnalysis: RiskAnalysis | null;
    extractedData: ExtractedData | null;
}

export const DrugInfoSection: React.FC<DrugInfoSectionProps> = ({ riskAnalysis, extractedData }) => {
    // Search State
    const [query, setQuery] = useState('');
    const [searchResult, setSearchResult] = useState<DrugInfoResult | null>(null);
    const [searching, setSearching] = useState(false);

    // Recommendations State
    const [recommendations, setRecommendations] = useState<DrugRecommendation | null>(null);
    const [loadingRecs, setLoadingRecs] = useState(false);

    const handleSearch = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!query) return;
        setSearching(true);
        try {
            const res = await axios.get(`/api/drug-info?query=${encodeURIComponent(query)}`);
            setSearchResult(res.data);
        } catch (err) {
            console.error(err);
        } finally {
            setSearching(false);
        }
    };

    const getRecommendations = async () => {
        if (!riskAnalysis?.risk_score || !extractedData) return;
        setLoadingRecs(true);
        try {
            const res = await axios.post('/api/drug-recommendations', {
                data: extractedData,
                risk_score: riskAnalysis.risk_score,
                shap_features: riskAnalysis.shap_values
            });
            setRecommendations(res.data);
        } catch (err) {
            console.error(err);
        } finally {
            setLoadingRecs(false);
        }
    };

    return (
        <section id="drugs" className="mb-16">

            <h2 className="text-3xl font-black mb-8 flex items-center gap-3">
                <span className="bg-secondary text-white p-2 rounded-lg shadow-pop rotate-3">💊</span>
                Drug Information & Recommendations
            </h2>

            <div className="grid md:grid-cols-2 gap-8">

                {/* Lookup Column */}
                <div className="space-y-6">
                    <Card className="p-6 h-full">
                        <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                            <Search className="text-accent" /> Drug Lookup
                        </h3>
                        <form onSubmit={handleSearch} className="flex gap-2 mb-6">
                            <Input
                                placeholder="e.g. Metformin, Headache..."
                                value={query}
                                onChange={(e) => setQuery(e.target.value)}
                            />
                            <Button type="submit" disabled={searching}>
                                {searching ? "..." : "Search"}
                            </Button>
                        </form>

                        {searchResult && (
                            <div className="bg-slate-50 p-4 rounded-xl border-2 border-slate-100 animate-popIn">
                                <h4 className="font-bold text-lg text-accent mb-2">{searchResult.drug_name}</h4>
                                <div className="prose prose-sm prose-slate leading-relaxed">
                                    {/* Render pre-formatted text from backend carefully */}
                                    <p className="whitespace-pre-line">{searchResult.data}</p>
                                </div>
                            </div>
                        )}
                    </Card>
                </div>

                {/* Recommendations Column */}
                <div className="space-y-6 relative animate-fadeIn">
                    <Card variant="featured" className="p-6 h-full border-dashed bg-blue-50/50">
                        <div className="flex justify-between items-start mb-6">
                            <div>
                                <h3 className="text-xl font-bold flex items-center gap-2">
                                    <Pill className="text-secondary" /> Personal Recommendations
                                </h3>
                                <p className="text-sm text-muted-foreground mt-1">Based on patient risk profile.</p>
                            </div>
                            {riskAnalysis ? (
                                <Button onClick={getRecommendations} disabled={loadingRecs} size="sm" variant="secondary">
                                    {loadingRecs ? "Generating..." : "Generate Guide"}
                                </Button>
                            ) : (
                                <span className="text-xs font-bold bg-slate-200 px-2 py-1 rounded text-slate-500">Risk Assessment Required</span>
                            )}
                        </div>

                        {recommendations && (
                            <div className="space-y-4 animate-popIn">
                                {recommendations.message && (
                                    <div className="bg-white p-3 rounded-lg border-l-4 border-blue-500 text-sm font-medium shadow-sm">
                                        <Info size={16} className="inline mr-2 text-blue-500" />
                                        {recommendations.message}
                                    </div>
                                )}

                                {recommendations.drugs?.map((drug, idx) => (
                                    <div key={idx} className="bg-white p-4 rounded-xl border-2 border-slate-200 shadow-sm hover:border-secondary transition-colors cursor-pointer group">
                                        <div className="flex justify-between items-center mb-2">
                                            <h4 className="font-bold text-lg group-hover:text-secondary transition-colors">{drug.name}</h4>
                                            <span className="text-xs font-bold bg-slate-100 px-2 py-1 rounded uppercase tracking-wide text-slate-500">{drug.brand_names[0]}</span>
                                        </div>
                                        <p className="text-sm text-slate-600 line-clamp-2">{drug.purpose}</p>
                                    </div>
                                ))}

                                <p className="text-xs text-center text-muted-foreground mt-4 font-medium opacity-70">
                                    ⚠️ Disclaimer: {recommendations.disclaimer || "Consult a healthcare professional."}
                                </p>
                            </div>
                        )}

                        {!riskAnalysis && (
                            <div className="flex flex-col items-center justify-center h-48 text-slate-400">
                                <Info size={48} className="mb-4 opacity-20" />
                                <p className="text-sm font-medium">Complete risk assessment to unlock recommendations.</p>
                            </div>
                        )}
                    </Card>
                </div>

            </div>
        </section>
    );
};
