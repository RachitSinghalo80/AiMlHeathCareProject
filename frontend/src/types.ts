export interface ExtractedData {
    [key: string]: any;
}

export interface RiskAnalysis {
    risk_score: number;
    risk_level: string;
    shap_values: Record<string, number>;
    top_factors: [string, number][];
    grouped_features: Record<string, [string, number][]>;
}

export interface DrugRecommendation {
    has_recommendations: boolean;
    message?: string;
    disclaimer?: string;
    drugs: Array<{
        name: string;
        brand_names: string[];
        manufacturer: string;
        purpose: string;
        dosage: string;
        warnings: string;
        side_effects: string;
        contraindications: string;
        drug_interactions: string;
        found: boolean;
    }>;
}

export interface DrugInfoResult {
    drug_name: string;
    data: string;
    success: boolean;
}
