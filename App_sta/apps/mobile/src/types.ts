export type RootStackParamList = {
  Login: undefined;
  Register: undefined;
  Dashboard: undefined;
  Dataset: { datasetId: string; datasetName: string };
  Analysis: { datasetId: string; column: string; datasetName: string };
  Methods: { datasetId: string; datasetName: string };
  MethodAnalysis: { datasetId: string; datasetName: string; method: MethodId };
  Learning: undefined;
  History: undefined;
};

export type User = {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  created_at: string;
};

export type TokenResponse = {
  access_token: string;
  refresh_token: string;
  token_type: 'bearer';
};

export type MethodId = 'ttest' | 'anova' | 'chi_square' | 'fisher' | 'vif' | 'breusch_pagan' | 'ols' | 'logit' | 'probit';

export type DatasetColumn = {
  name: string;
  position: number;
  data_type: string;
  missing_count: number;
  unique_count: number;
};

export type Dataset = {
  id: string;
  name: string;
  row_count: number;
  column_count: number;
  delimiter: string;
  encoding: string;
  created_at: string;
  columns: DatasetColumn[];
};

export type DatasetPreview = {
  dataset_id: string;
  columns: string[];
  rows: Record<string, string | number | boolean | null>[];
  page: number;
  page_size: number;
  total_rows: number;
};

export type DescriptiveResult = {
  dataset_id: string;
  variable: string;
  count: number;
  mean: number;
  median: number;
  modes: number[];
  variance: number;
  standard_deviation: number;
  coefficient_of_variation: number | null;
  warnings: string[];
  interpretation: { result: string; interpretation: string; pedagogical: string };
};

export type LearningMethod = {
  id: string;
  name: string;
  definition: string;
  formula: string;
  utility: string;
  conditions: string[];
  example: string;
  commands: { software: string; command: string }[];
};

export type LearningModule = {
  id: string;
  name: string;
  description: string;
  methods: LearningMethod[];
};

export type ProgressSummary = {
  methods_started: number;
  methods_completed: number;
  average_completion: number;
  global_completion: number;
  modules: Record<string, number>;
};

export type AnalysisHistory = {
  id: string;
  dataset_id: string;
  analysis_type: string;
  dataset_name: string;
  parameters: Record<string, unknown>;
  results: Record<string, unknown>;
  engine_version: string;
  created_at: string;
};
