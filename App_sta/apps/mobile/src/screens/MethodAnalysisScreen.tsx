import { useEffect, useState } from 'react';
import { ActivityIndicator, Pressable, SafeAreaView, ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';

import { getDataset, getPreview, runMethod } from '../datasetApi';
import { colors, spacing } from '../theme';
import type { Dataset, DatasetPreview, MethodId, RootStackParamList } from '../types';

type Props = NativeStackScreenProps<RootStackParamList, 'MethodAnalysis'>;

const labels: Record<MethodId, string> = {
  ttest: 'TEST T', anova: 'ANOVA', chi_square: 'TEST DU CHI-DEUX', fisher: 'TEST EXACT DE FISHER',
  vif: 'FACTEUR VIF', breusch_pagan: 'BREUSCH-PAGAN', ols: 'RÉGRESSION OLS', logit: 'MODÈLE LOGIT', probit: 'MODÈLE PROBIT',
};
const help: Record<MethodId, string> = {
  ttest: 'Choisissez une variable quantitative et sa moyenne de référence.',
  anova: 'Sélectionnez la variable quantitative, puis la variable de groupes.',
  chi_square: 'Sélectionnez deux variables qualitatives.', fisher: 'Sélectionnez deux variables qualitatives pour une table 2×2.',
  vif: 'Sélectionnez au moins deux variables explicatives quantitatives.',
  breusch_pagan: 'Sélectionnez la variable dépendante, puis les explicatives quantitatives.',
  ols: 'Sélectionnez la variable dépendante, puis une ou plusieurs explicatives.',
  logit: 'Sélectionnez une cible codée 0/1, puis les explicatives quantitatives.',
  probit: 'Sélectionnez une cible codée 0/1, puis les explicatives quantitatives.',
};
const minimum: Record<MethodId, number> = { ttest: 1, anova: 2, chi_square: 2, fisher: 2, vif: 2, breusch_pagan: 2, ols: 2, logit: 2, probit: 2 };

export function MethodAnalysisScreen({ route }: Props) {
  const { datasetId, datasetName, method } = route.params;
  const [preview, setPreview] = useState<DatasetPreview | null>(null);
  const [dataset, setDataset] = useState<Dataset | null>(null);
  const [selected, setSelected] = useState<string[]>([]);
  const [reference, setReference] = useState('0');
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    Promise.all([getPreview(datasetId, 1), getDataset(datasetId)])
      .then(([loadedPreview, loadedDataset]) => { setPreview(loadedPreview); setDataset(loadedDataset); })
      .catch((caught) => setError(caught instanceof Error ? caught.message : 'Dataset indisponible.'))
      .finally(() => setLoading(false));
  }, [datasetId]);

  function toggle(column: string) { setSelected((current) => current.includes(column) ? current.filter((item) => item !== column) : [...current, column]); }

  async function submit() {
    if (selected.length < minimum[method]) { setError(`Sélectionnez au moins ${minimum[method]} variable${minimum[method] > 1 ? 's' : ''}.`); return; }
    setRunning(true); setError('');
    try { setResult(await runMethod(datasetId, method, selected, Number(reference))); }
    catch (caught) { setError(caught instanceof Error ? caught.message : 'Analyse impossible.'); }
    finally { setRunning(false); }
  }

  if (loading) return <SafeAreaView style={styles.safe}><ActivityIndicator color={colors.teal} size="large" /></SafeAreaView>;
  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.kicker}>{labels[method]}</Text>
        <Text style={styles.title}>{datasetName}</Text>
        <Text style={styles.help}>{help[method]}</Text>
        <Text style={styles.section}>Variables sélectionnées : {selected.length}</Text>
        {preview?.columns.map((column) => {
          const metadata = dataset?.columns.find((item) => item.name === column);
          return <Pressable accessibilityRole="button" key={column} onPress={() => toggle(column)} style={[styles.column, selected.includes(column) && styles.selected]}><View style={[styles.radio, selected.includes(column) && styles.radioSelected]} /><View><Text style={styles.columnText}>{column}</Text><Text style={styles.metadata}>{metadata?.data_type ?? 'type inconnu'} · {metadata?.missing_count ?? 0} valeur(s) manquante(s)</Text></View></Pressable>;
        })}
        {method === 'ttest' ? <View style={styles.reference}><Text style={styles.label}>Moyenne de référence</Text><TextInput keyboardType="numeric" onChangeText={setReference} style={styles.input} value={reference} /></View> : null}
        {error ? <Text style={styles.error}>{error}</Text> : null}
        <Pressable accessibilityRole="button" disabled={running} onPress={() => void submit()} style={styles.run}>{running ? <ActivityIndicator color={colors.surface} /> : <Text style={styles.runText}>Lancer l’analyse</Text>}</Pressable>
        {result ? <ResultView result={result} /> : null}
      </ScrollView>
    </SafeAreaView>
  );
}

function formatResultValue(value: unknown): string {
  if (typeof value === 'number' && Number.isFinite(value)) {
    return Number(value).toFixed(3);
  }
  if (Array.isArray(value)) {
    return value.map((item) => formatResultValue(item)).join(', ');
  }
  if (value !== null && typeof value === 'object') {
    return Object.entries(value as Record<string, unknown>)
      .map(([key, item]) => `${key}: ${formatResultValue(item)}`)
      .join(', ');
  }
  return String(value);
}

function isCoefficientEntry(value: unknown): value is Array<Record<string, unknown>> {
  return Array.isArray(value) && value.every((item) => item !== null && typeof item === 'object');
}

function CoefficientTable({ coefficients }: { coefficients: Array<Record<string, unknown>> }) {
  const rows = coefficients.map((row, index) => ({
    name: String(row.name ?? `col_${index + 1}`),
    coefficient: Number(row.coefficient ?? 0),
    standard_error: Number(row.standard_error ?? 0),
    statistic: Number(row.statistic ?? 0),
    p_value: Number(row.p_value ?? 0),
  }));

  return (
    <View style={styles.coefficientTableContainer}>
      <Text style={styles.resultTitle}>Coefficients</Text>
      {rows.map((row) => (
        <View key={row.name} style={styles.verticalCoefficientRow}>
          <Text style={styles.verticalCoefficientText}><Text style={styles.verticalCoefficientLabel}>Variable:</Text> <Text style={styles.verticalCoefficientValue}>{row.name}</Text></Text>
          <Text style={styles.verticalCoefficientText}><Text style={styles.verticalCoefficientLabel}>coef:</Text> {row.coefficient.toFixed(3)}</Text>
          <Text style={styles.verticalCoefficientText}><Text style={styles.verticalCoefficientLabel}>SE:</Text> {row.standard_error.toFixed(3)}</Text>
          <Text style={styles.verticalCoefficientText}><Text style={styles.verticalCoefficientLabel}>Stat:</Text> {row.statistic.toFixed(3)}</Text>
          <Text style={styles.verticalCoefficientText}><Text style={styles.verticalCoefficientLabel}>p-value:</Text> {row.p_value.toFixed(3)}</Text>
        </View>
      ))}
    </View>
  );
}

function ResultView({ result }: { result: Record<string, unknown> }) {
  const interpretation = result.interpretation as Record<string, string> | undefined;
  const coefficients = isCoefficientEntry(result.coefficients) ? result.coefficients : null;

  return (
    <View style={styles.result}>
      <Text style={styles.resultTitle}>Résultats</Text>
      {coefficients ? <CoefficientTable coefficients={coefficients} /> : null}
      {Object.entries(result).filter(([key]) => !['interpretation', 'warnings', 'dataset_id', 'variables', 'coefficients'].includes(key)).map(([key, value]) => (
        <View key={key} style={styles.resultRow}>
          <Text style={styles.resultKey}>{key.replaceAll('_', ' ')}</Text>
          <Text style={styles.resultValue}>{formatResultValue(value)}</Text>
        </View>
      ))}
      {interpretation ? <><Text style={styles.resultTitle}>Interprétation</Text>{Object.values(interpretation).map((text) => <Text key={text} style={styles.interpretation}>{text}</Text>)}</> : null}
      {Array.isArray(result.warnings) ? result.warnings.map((warning) => <Text key={String(warning)} style={styles.warning}>{String(warning)}</Text>) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  safe: { backgroundColor: colors.paper, flex: 1 }, content: { padding: spacing.lg }, kicker: { color: colors.coral, fontSize: 12, fontWeight: '800', letterSpacing: 1.5 }, title: { color: colors.ink, fontSize: 28, fontWeight: '800', marginTop: spacing.sm }, help: { color: colors.muted, fontSize: 15, lineHeight: 22, marginTop: spacing.sm }, section: { color: colors.ink, fontSize: 20, fontWeight: '800', marginBottom: spacing.sm, marginTop: spacing.xl }, column: { alignItems: 'center', backgroundColor: colors.surface, borderColor: colors.line, borderRadius: 8, borderWidth: 1, flexDirection: 'row', marginBottom: spacing.sm, padding: spacing.md }, selected: { backgroundColor: colors.tealSoft, borderColor: colors.teal }, radio: { borderColor: colors.muted, borderRadius: 10, borderWidth: 2, height: 20, marginRight: spacing.sm, width: 20 }, radioSelected: { backgroundColor: colors.teal, borderColor: colors.teal }, columnText: { color: colors.ink, fontSize: 16, fontWeight: '700' }, metadata: { color: colors.muted, fontSize: 12, marginTop: 3 }, reference: { gap: spacing.xs, marginTop: spacing.md }, label: { color: colors.ink, fontSize: 14, fontWeight: '700' }, input: { backgroundColor: colors.surface, borderColor: colors.line, borderRadius: 8, borderWidth: 1, color: colors.ink, fontSize: 16, minHeight: 50, paddingHorizontal: spacing.md }, error: { color: colors.danger, fontSize: 14, lineHeight: 20, marginTop: spacing.md }, run: { alignItems: 'center', backgroundColor: colors.teal, borderRadius: 8, justifyContent: 'center', marginTop: spacing.lg, minHeight: 52 }, runText: { color: colors.surface, fontSize: 16, fontWeight: '800' }, result: { backgroundColor: colors.surface, borderColor: colors.line, borderRadius: 10, borderWidth: 1, marginTop: spacing.xl, padding: spacing.lg }, resultTitle: { color: colors.ink, fontSize: 20, fontWeight: '800', marginBottom: spacing.md, marginTop: spacing.sm }, resultRow: { borderBottomColor: colors.line, borderBottomWidth: 1, paddingVertical: spacing.sm }, resultKey: { color: colors.muted, fontSize: 13, textTransform: 'capitalize' }, resultValue: { color: colors.ink, fontSize: 16, fontWeight: '700', marginTop: 2 }, interpretation: { color: colors.muted, fontSize: 15, lineHeight: 23, marginBottom: spacing.sm }, warning: { backgroundColor: colors.amberSoft, color: colors.amber, fontSize: 14, lineHeight: 20, marginTop: spacing.sm, padding: spacing.sm },
});
