import { authenticatedRequest } from './api';
import { Platform } from 'react-native';
import type { AnalysisHistory, Dataset, DatasetPreview, DescriptiveResult, LearningModule, MethodId, ProgressSummary } from './types';

export async function listDatasets(): Promise<Dataset[]> {
  return authenticatedRequest<Dataset[]>('/datasets');
}

export async function uploadDataset(uri: string, name: string, mimeType = 'text/csv'): Promise<Dataset> {
  const form = new FormData();
  if (Platform.OS === 'web') {
    const fileResponse = await fetch(uri);
    if (!fileResponse.ok) throw new Error('Le fichier selectionne ne peut pas etre lu.');
    const blob = await fileResponse.blob();
    form.append('file', new File([blob], name, { type: mimeType }));
  } else {
    form.append('file', { uri, name, type: mimeType } as unknown as Blob);
  }
  return authenticatedRequest<Dataset>('/datasets', {
    method: 'POST',
    body: form,
  });
}

export async function getPreview(datasetId: string, pageSize = 25): Promise<DatasetPreview> {
  return authenticatedRequest<DatasetPreview>(`/datasets/${datasetId}/preview?page_size=${pageSize}`);
}

export async function getDataset(datasetId: string): Promise<Dataset> {
  return authenticatedRequest<Dataset>(`/datasets/${datasetId}`);
}

export async function calculateDescriptive(datasetId: string, column: string): Promise<DescriptiveResult> {
  return authenticatedRequest<DescriptiveResult>('/statistics/descriptive', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ dataset_id: datasetId, column }),
  });
}

export async function runOneSampleTTest(datasetId: string, column: string, populationMean: number): Promise<Record<string, unknown>> {
  return authenticatedRequest<Record<string, unknown>>('/tests/ttest', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ dataset_id: datasetId, test_type: 'one_sample', column, population_mean: populationMean }),
  });
}

export async function runOls(datasetId: string, dependentColumn: string, explanatoryColumns: string[]): Promise<Record<string, unknown>> {
  return authenticatedRequest<Record<string, unknown>>('/models/ols', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ dataset_id: datasetId, dependent_column: dependentColumn, explanatory_columns: explanatoryColumns }),
  });
}

export async function runMethod(datasetId: string, method: MethodId, selectedColumns: string[], reference = 0): Promise<Record<string, unknown>> {
  const [first, second] = selectedColumns;
  const endpoints: Record<MethodId, string> = { ttest: '/tests/ttest', anova: '/tests/anova', chi_square: '/tests/chi-square', fisher: '/tests/fisher', vif: '/tests/vif', breusch_pagan: '/tests/breusch-pagan', ols: '/models/ols', logit: '/models/logit', probit: '/models/probit' };
  const body = method === 'ttest' ? { dataset_id: datasetId, test_type: 'one_sample', column: first, population_mean: reference } : method === 'anova' ? { dataset_id: datasetId, value_column: first, group_column: second } : method === 'chi_square' || method === 'fisher' ? { dataset_id: datasetId, first_column: first, second_column: second, test_type: method } : method === 'vif' ? { dataset_id: datasetId, columns: selectedColumns } : method === 'breusch_pagan' ? { dataset_id: datasetId, dependent_column: first, columns: selectedColumns.slice(1) } : method === 'ols' ? { dataset_id: datasetId, dependent_column: first, explanatory_columns: selectedColumns.slice(1) } : { dataset_id: datasetId, dependent_column: first, explanatory_columns: selectedColumns.slice(1), model_type: method };
  return authenticatedRequest<Record<string, unknown>>(endpoints[method], { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
}

export async function listLearningModules(): Promise<LearningModule[]> {
  return authenticatedRequest<LearningModule[]>('/modules');
}

export async function getProgress(): Promise<ProgressSummary> {
  return authenticatedRequest<ProgressSummary>('/progress');
}

export async function markMethodStarted(methodId: string): Promise<void> {
  await authenticatedRequest(`/progress/${methodId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ completion: 10 }),
  });
}

export async function listAnalysisHistory(limit = 25): Promise<AnalysisHistory[]> {
  return authenticatedRequest<AnalysisHistory[]>(`/analysis/history?limit=${limit}`);
}
