import { apiGet } from "./apiClient";

export interface AIPreferenceCategory {
  category: string;
  confidence: number;
  semanticSimilarity: number;
  behaviorScore: number;
  actionMix: Record<string, number>;
  evidenceProducts: Array<{
    productId: string;
    productName: string;
    score: number;
  }>;
}

export interface AIPreferenceItem {
  userId: string;
  primaryCategory: string | null;
  primaryConfidence: number;
  categories: AIPreferenceCategory[];
}

export interface AIPreferenceResponse {
  model: {
    name: string;
    mode: string;
    cacheDir: string;
    loaded: boolean;
    loadError?: string | null;
  };
  behaviorWeights: Record<string, number>;
  items: AIPreferenceItem[];
  generatedAt: string;
}

export const aiPreferenceApi = {
  preferenceCategories: () => apiGet<AIPreferenceResponse>("/ai/preference-categories"),
};
