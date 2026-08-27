import * as DocumentPicker from 'expo-document-picker';
import { useCallback, useEffect, useState } from 'react';
import { ActivityIndicator, Pressable, SafeAreaView, ScrollView, StyleSheet, Text, View } from 'react-native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';

import { useAuth } from '../auth';
import { getProgress, listDatasets, uploadDataset } from '../datasetApi';
import { colors, spacing } from '../theme';
import type { Dataset, RootStackParamList } from '../types';
import type { ProgressSummary } from '../types';

type Props = NativeStackScreenProps<RootStackParamList, 'Dashboard'>;

export function DashboardScreen({ navigation }: Props) {
  const { user, signOut } = useAuth();
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [progress, setProgress] = useState<ProgressSummary | null>(null);

  const refreshDatasets = useCallback(async () => {
    setLoading(true);
    try {
      const [loadedDatasets, loadedProgress] = await Promise.all([listDatasets(), getProgress()]);
      setDatasets(loadedDatasets);
      setProgress(loadedProgress);
      setError('');
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Datasets indisponibles.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { void refreshDatasets(); }, [refreshDatasets]);

  async function pickAndUpload() {
    const picked = await DocumentPicker.getDocumentAsync({ type: 'text/csv', copyToCacheDirectory: true });
    if (picked.canceled) return;
    setUploading(true);
    setError('');
    try {
      await uploadDataset(picked.assets[0].uri, picked.assets[0].name, picked.assets[0].mimeType ?? 'text/csv');
      await refreshDatasets();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Import impossible.');
    } finally {
      setUploading(false);
    }
  }

  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.content}>
        <View style={styles.topline}>
          <View><Text style={styles.kicker}>TABLEAU DE BORD</Text><Text style={styles.greeting}>Bonjour, {user?.first_name}.</Text></View>
          <Text style={styles.avatar}>{user?.first_name.charAt(0).toUpperCase()}</Text>
        </View>
        <View style={styles.hero}><Text style={styles.heroLabel}>VOTRE PARCOURS</Text><Text style={styles.heroTitle}>De la question aux résultats.</Text><Text style={styles.heroText}>Importez un fichier CSV, explorez ses variables et lancez votre première analyse.</Text></View>
        <Pressable accessibilityRole="button" onPress={() => navigation.navigate('Learning')} style={styles.hero}><Text style={styles.heroTitle}>Parcours d’apprentissage</Text><Text style={styles.heroText}>Définitions, formules, conditions et commandes.</Text></Pressable>
        {progress ? <View style={styles.progress}><View style={styles.progressTop}><Text style={styles.progressTitle}>Votre progression</Text><Text style={styles.progressValue}>{Math.round(progress.global_completion)}%</Text></View><View style={styles.track}><View style={[styles.fill, { width: `${progress.global_completion}%` }]} /></View><Text style={styles.progressText}>{progress.methods_completed} méthode{progress.methods_completed > 1 ? 's' : ''} terminée{progress.methods_completed > 1 ? 's' : ''} · {progress.methods_started} commencée{progress.methods_started > 1 ? 's' : ''}</Text><Text style={styles.progressText}>Descriptif : {Math.round(progress.modules.descriptive ?? 0)}%  ·  Inférentiel : {Math.round(progress.modules.inference ?? 0)}%  ·  Économétrie : {Math.round(progress.modules.econometrics ?? 0)}%</Text></View> : null}
        <Pressable accessibilityRole="button" onPress={() => navigation.navigate('History')} style={styles.importRow}><View><Text style={styles.importTitle}>Analyses récentes</Text><Text style={styles.importText}>Retrouver vos résultats enregistrés</Text></View><Text style={styles.chevron}>›</Text></Pressable>
        <View style={styles.importRow}><View><Text style={styles.importTitle}>Nouveau dataset</Text><Text style={styles.importText}>Ajoutez vos données au format CSV.</Text></View><Pressable accessibilityRole="button" disabled={uploading} onPress={() => void pickAndUpload()} style={styles.importButton}>{uploading ? <ActivityIndicator color={colors.surface} /> : <Text style={styles.importButtonText}>Importer</Text>}</Pressable></View>
        {error ? <Text style={styles.error}>{error}</Text> : null}
        <Text style={styles.sectionTitle}>Mes datasets</Text>
        {loading ? <ActivityIndicator color={colors.teal} /> : datasets.length === 0 ? <View style={styles.empty}><Text style={styles.emptyTitle}>Votre espace est prêt.</Text><Text style={styles.emptyText}>Importez un CSV pour commencer à apprendre sur des données réelles.</Text></View> : datasets.map((dataset) => <Pressable accessibilityRole="button" key={dataset.id} onPress={() => navigation.navigate('Dataset', { datasetId: dataset.id, datasetName: dataset.name })} style={styles.dataset}><View style={styles.datasetTop}><Text style={styles.datasetName}>{dataset.name}</Text><Text style={styles.chevron}>›</Text></View><Text style={styles.datasetMeta}>{dataset.row_count} observations  ·  {dataset.column_count} variables</Text><Text style={styles.datasetAction}>Explorer les données</Text></Pressable>)}
        <Pressable accessibilityRole="button" onPress={() => void signOut()}><Text style={styles.logout}>Se déconnecter</Text></Pressable>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { backgroundColor: colors.paper, flex: 1 }, content: { padding: spacing.lg }, topline: { alignItems: 'center', flexDirection: 'row', justifyContent: 'space-between', marginBottom: spacing.xl }, kicker: { color: colors.coral, fontSize: 12, fontWeight: '800', letterSpacing: 1.5 }, greeting: { color: colors.ink, fontSize: 25, fontWeight: '800', marginTop: spacing.xs }, avatar: { backgroundColor: colors.ink, borderRadius: 24, color: colors.surface, fontSize: 18, fontWeight: '800', height: 48, paddingTop: 12, textAlign: 'center', width: 48 }, hero: { backgroundColor: colors.ink, borderRadius: 12, marginBottom: spacing.md, padding: spacing.lg }, heroLabel: { color: '#9FD8D0', fontSize: 11, fontWeight: '800', letterSpacing: 1.5 }, heroTitle: { color: colors.surface, fontSize: 27, fontWeight: '800', lineHeight: 32, marginTop: spacing.sm }, heroText: { color: '#C4D4D8', fontSize: 15, lineHeight: 22, marginTop: spacing.md }, learning: { backgroundColor: colors.coralSoft, borderRadius: 10, marginBottom: spacing.md, padding: spacing.md }, learningTitle: { color: colors.ink, fontSize: 16, fontWeight: '800' }, learningText: { color: colors.muted, fontSize: 13, marginTop: 3 }, progress: { backgroundColor: colors.surface, borderColor: colors.line, borderRadius: 10, borderWidth: 1, marginBottom: spacing.md, padding: spacing.md }, progressTop: { alignItems: 'center', flexDirection: 'row', justifyContent: 'space-between' }, progressTitle: { color: colors.ink, fontSize: 16, fontWeight: '800' }, progressValue: { color: colors.teal, fontSize: 20, fontWeight: '800' }, track: { backgroundColor: colors.tealSoft, borderRadius: 5, height: 8, marginTop: spacing.sm, overflow: 'hidden' }, fill: { backgroundColor: colors.teal, borderRadius: 5, height: 8 }, progressText: { color: colors.muted, fontSize: 13, marginTop: spacing.sm }, importRow: { alignItems: 'center', backgroundColor: colors.tealSoft, borderRadius: 10, flexDirection: 'row', justifyContent: 'space-between', padding: spacing.md }, importTitle: { color: colors.ink, fontSize: 16, fontWeight: '800' }, importText: { color: colors.muted, fontSize: 13, marginTop: 3 }, importButton: { alignItems: 'center', backgroundColor: colors.teal, borderRadius: 8, justifyContent: 'center', minHeight: 42, paddingHorizontal: spacing.md }, importButtonText: { color: colors.surface, fontSize: 14, fontWeight: '800' }, error: { color: colors.danger, fontSize: 14, lineHeight: 20, marginTop: spacing.md }, sectionTitle: { color: colors.ink, fontSize: 20, fontWeight: '800', marginBottom: spacing.md, marginTop: spacing.xl }, empty: { backgroundColor: colors.surface, borderColor: colors.line, borderRadius: 10, borderWidth: 1, padding: spacing.lg }, emptyTitle: { color: colors.ink, fontSize: 17, fontWeight: '800' }, emptyText: { color: colors.muted, fontSize: 15, lineHeight: 22, marginTop: spacing.xs }, dataset: { backgroundColor: colors.surface, borderColor: colors.line, borderRadius: 10, borderWidth: 1, marginBottom: spacing.md, padding: spacing.md }, datasetTop: { alignItems: 'center', flexDirection: 'row', justifyContent: 'space-between' }, datasetName: { color: colors.ink, flex: 1, fontSize: 16, fontWeight: '800' }, chevron: { color: colors.teal, fontSize: 28, lineHeight: 28 }, datasetMeta: { color: colors.muted, fontSize: 13, marginTop: spacing.xs }, datasetAction: { color: colors.teal, fontSize: 13, fontWeight: '800', marginTop: spacing.md }, logout: { color: colors.muted, fontSize: 14, fontWeight: '700', marginBottom: spacing.lg, marginTop: spacing.lg, textAlign: 'center' },
});
