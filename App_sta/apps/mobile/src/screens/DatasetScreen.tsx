import * as DocumentPicker from 'expo-document-picker';
import { useEffect, useState } from 'react';
import { ActivityIndicator, Pressable, SafeAreaView, ScrollView, StyleSheet, Text, View } from 'react-native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';

import { getPreview, uploadDataset } from '../datasetApi';
import { colors, spacing } from '../theme';
import type { DatasetPreview, RootStackParamList } from '../types';

type Props = NativeStackScreenProps<RootStackParamList, 'Dataset'>;

export function DatasetScreen({ route, navigation }: Props) {
  const { datasetId, datasetName } = route.params;
  const [preview, setPreview] = useState<DatasetPreview | null>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getPreview(datasetId).then(setPreview).catch((caught) => setError(caught instanceof Error ? caught.message : 'Aperçu indisponible.')).finally(() => setLoading(false));
  }, [datasetId]);

  return <SafeAreaView style={styles.safe}><ScrollView contentContainerStyle={styles.content}><Text style={styles.kicker}>EXPLORATEUR DE DONNÉES</Text><Text style={styles.title}>{datasetName}</Text>{loading ? <ActivityIndicator color={colors.teal} size="large" /> : error ? <Text style={styles.error}>{error}</Text> : preview ? <><View style={styles.summary}><Text style={styles.summaryValue}>{preview.total_rows}</Text><Text style={styles.summaryLabel}>observations</Text><Text style={styles.summaryValue}>{preview.columns.length}</Text><Text style={styles.summaryLabel}>variables</Text></View><Pressable accessibilityRole="button" onPress={() => navigation.navigate('Methods', { datasetId, datasetName })} style={styles.methodsButton}><Text style={styles.methodsTitle}>Choisir une méthode</Text><Text style={styles.methodsText}>Test t et régression linéaire OLS</Text></Pressable><Text style={styles.sectionTitle}>Aperçu</Text><ScrollView horizontal showsHorizontalScrollIndicator={false}><View><View style={styles.row}>{preview.columns.map((column) => <Text key={column} style={[styles.cell, styles.header]}>{column}</Text>)}</View>{preview.rows.map((row, index) => <View key={index} style={styles.row}>{preview.columns.map((column) => <Text key={column} style={styles.cell}>{String(row[column] ?? '—')}</Text>)}</View>)}</View></ScrollView><Text style={styles.sectionTitle}>Analyser une variable</Text>{preview.columns.map((column) => <Pressable key={column} accessibilityRole="button" onPress={() => navigation.navigate('Analysis', { datasetId, column, datasetName })} style={styles.columnButton}><Text style={styles.columnName}>{column}</Text><Text style={styles.columnAction}>Calculer les statistiques  →</Text></Pressable>)}</> : null}</ScrollView></SafeAreaView>;
}

export async function pickCsv(): Promise<DocumentPicker.DocumentPickerAsset | null> {
  const result = await DocumentPicker.getDocumentAsync({ type: 'text/csv', copyToCacheDirectory: true });
  return result.canceled ? null : result.assets[0];
}

const styles = StyleSheet.create({ safe: { backgroundColor: colors.paper, flex: 1 }, content: { padding: spacing.lg }, kicker: { color: colors.coral, fontSize: 12, fontWeight: '800', letterSpacing: 1.5, marginBottom: spacing.sm }, title: { color: colors.ink, fontSize: 28, fontWeight: '800', marginBottom: spacing.xl }, error: { color: colors.danger, fontSize: 15, lineHeight: 22 }, summary: { alignItems: 'center', backgroundColor: colors.ink, borderRadius: 12, flexDirection: 'row', gap: spacing.sm, marginBottom: spacing.md, padding: spacing.lg }, summaryValue: { color: colors.surface, fontSize: 25, fontWeight: '800' }, summaryLabel: { color: '#C4D4D8', fontSize: 14, marginRight: spacing.md }, methodsButton: { backgroundColor: colors.coralSoft, borderRadius: 10, padding: spacing.md }, methodsTitle: { color: colors.ink, fontSize: 17, fontWeight: '800' }, methodsText: { color: colors.muted, fontSize: 14, marginTop: spacing.xs }, sectionTitle: { color: colors.ink, fontSize: 20, fontWeight: '800', marginBottom: spacing.md, marginTop: spacing.lg }, row: { flexDirection: 'row' }, cell: { borderBottomColor: colors.line, borderBottomWidth: 1, color: colors.ink, minWidth: 110, padding: spacing.sm }, header: { backgroundColor: colors.tealSoft, fontWeight: '800' }, columnButton: { backgroundColor: colors.surface, borderColor: colors.line, borderRadius: 8, borderWidth: 1, marginBottom: spacing.sm, padding: spacing.md }, columnName: { color: colors.ink, fontSize: 16, fontWeight: '800' }, columnAction: { color: colors.teal, fontSize: 13, fontWeight: '700', marginTop: spacing.xs } });
