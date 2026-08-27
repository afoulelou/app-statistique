import { useEffect, useState } from 'react';
import { ActivityIndicator, SafeAreaView, ScrollView, StyleSheet, Text, View } from 'react-native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';

import { calculateDescriptive } from '../datasetApi';
import { colors, spacing } from '../theme';
import type { DescriptiveResult, RootStackParamList } from '../types';

type Props = NativeStackScreenProps<RootStackParamList, 'Analysis'>;

export function AnalysisScreen({ route }: Props) {
  const { datasetId, column, datasetName } = route.params;
  const [result, setResult] = useState<DescriptiveResult | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    calculateDescriptive(datasetId, column).then(setResult).catch((caught) => setError(caught instanceof Error ? caught.message : 'Analyse impossible.'));
  }, [datasetId, column]);

  if (error) return <SafeAreaView style={styles.safe}><View style={styles.content}><Text style={styles.kicker}>ANALYSE IMPOSSIBLE</Text><Text style={styles.error}>{error}</Text></View></SafeAreaView>;
  if (!result) return <SafeAreaView style={styles.safe}><ActivityIndicator color={colors.teal} size="large" /></SafeAreaView>;

  return <SafeAreaView style={styles.safe}><ScrollView contentContainerStyle={styles.content}><Text style={styles.kicker}>RÉSULTAT DESCRIPTIF</Text><Text style={styles.title}>{column}</Text><Text style={styles.dataset}>{datasetName}</Text><View style={styles.metrics}><Metric label="Moyenne" value={result.mean.toFixed(2)} /><Metric label="Médiane" value={result.median.toFixed(2)} /><Metric label="Écart-type" value={result.standard_deviation.toFixed(2)} /><Metric label="N" value={String(result.count)} /></View><View style={styles.panel}><Text style={styles.panelTitle}>Résultat statistique</Text><Text style={styles.body}>{result.interpretation.result}</Text></View><View style={styles.panel}><Text style={styles.panelTitle}>Interprétation</Text><Text style={styles.body}>{result.interpretation.interpretation}</Text></View><View style={styles.pedagogy}><Text style={styles.panelTitle}>À retenir</Text><Text style={styles.body}>{result.interpretation.pedagogical}</Text></View>{result.warnings.map((warning) => <Text key={warning} style={styles.warning}>{warning}</Text>)}</ScrollView></SafeAreaView>;
}

function Metric({ label, value }: { label: string; value: string }) { return <View style={styles.metric}><Text style={styles.metricValue}>{value}</Text><Text style={styles.metricLabel}>{label}</Text></View>; }

const styles = StyleSheet.create({ safe: { backgroundColor: colors.paper, flex: 1 }, content: { padding: spacing.lg }, kicker: { color: colors.coral, fontSize: 12, fontWeight: '800', letterSpacing: 1.5 }, title: { color: colors.ink, fontSize: 30, fontWeight: '800', marginTop: spacing.sm }, dataset: { color: colors.muted, fontSize: 15, marginTop: spacing.xs }, metrics: { backgroundColor: colors.ink, borderRadius: 12, flexDirection: 'row', flexWrap: 'wrap', marginTop: spacing.xl, padding: spacing.md }, metric: { padding: spacing.sm, width: '50%' }, metricValue: { color: colors.surface, fontSize: 25, fontWeight: '800' }, metricLabel: { color: '#C4D4D8', fontSize: 13, marginTop: 3 }, panel: { backgroundColor: colors.surface, borderColor: colors.line, borderRadius: 10, borderWidth: 1, marginTop: spacing.md, padding: spacing.lg }, pedagogy: { backgroundColor: colors.tealSoft, borderRadius: 10, marginTop: spacing.md, padding: spacing.lg }, panelTitle: { color: colors.ink, fontSize: 18, fontWeight: '800', marginBottom: spacing.sm }, body: { color: colors.muted, fontSize: 15, lineHeight: 23 }, warning: { backgroundColor: colors.amberSoft, color: colors.amber, fontSize: 14, lineHeight: 20, marginTop: spacing.md, padding: spacing.md }, error: { color: colors.danger, fontSize: 16, lineHeight: 24 } });
