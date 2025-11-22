export interface MarketData {
  Japan: number;
  China: number;
  USA: number;
  Germany: number;
  Taiwan: number;
  USDCNY: number;
  USDJPY: number;
  Gold: number;
  VIX: number;
  SP500?: number;
  Nikkei225?: number;
  DAX?: number;
  TAIEX?: number;
  HangSeng?: number;
  [key: string]: number | undefined; // Index signature for dynamic access
}

export interface Strategy {
  probabilities: number[];
  dominantAction: number;
}

export interface CountryProxy {
  index: string;
  ticker: string;
  symbol: string;
}

export interface NashEquilibrium {
  date: string;
  strategies: number[][];
  parties: string[];
  actions: string[];
  dominant_actions: string[];
  global_scenario: string;
  market_context: MarketData;
  prices?: Record<string, number>;
  country_proxies?: Record<string, CountryProxy>;
}

export interface BacktestResult {
  date: string;
  predicted_scenario: string;
  actual_risk_off_next_week: boolean;
  hawk_dominant: boolean;
  japan_action: string;
  china_action: string;
  usa_action: string;
  germany_action: string;
  taiwan_action: string;
}

export interface BacktestSummary {
  total_weeks: number;
  accuracy: number;
  hawk_weeks_predicted: number;
  actual_risk_off_weeks: number;
}

export interface SensitivityResult {
  noise_level: number;
  noise_scaled: number;
  Japan_Hawk: number;
  China_Hawk: number;
  USA_Hawk: number;
  Germany_Deescalate: number;
  Taiwan_Deescalate: number;
  Global_Hawk_Scenario: number;
  Global_Deescalate_Scenario: number;
}

