import { Pressable, SafeAreaView, ScrollView, StyleSheet, Text, View } from 'react-native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';

import { colors, spacing } from '../theme';
import type { RootStackParamList } from '../types';

type Props = NativeStackScreenProps<RootStackParamList, 'Methods'>;

export function MethodsScreen({ route, navigation }: Props) {
  const { datasetId, datasetName } = route.params;
  const methods = [
    { id: 'ttest' as const, number: '01', title: 'Test t', description: 'Comparer une moyenne à une valeur de référence.', color: colors.teal, background: colors.tealSoft },
    { id: 'anova' as const, number: '02', title: 'ANOVA', description: 'Comparer les moyennes de plusieurs groupes.', color: colors.coral, background: colors.coralSoft },
    { id: 'chi_square' as const, number: '03', title: 'Test du Chi-deux', description: 'Tester l’association entre deux variables qualitatives.', color: colors.amber, background: colors.amberSoft },
    { id: 'fisher' as const, number: '04', title: 'Test exact de Fisher', description: 'Tester une association dans une table 2×2.', color: colors.teal, background: colors.tealSoft },
    { id: 'vif' as const, number: '05', title: 'Facteur VIF', description: 'Diagnostiquer la multicolinéarité.', color: colors.coral, background: colors.coralSoft },
    { id: 'breusch_pagan' as const, number: '06', title: 'Breusch-Pagan', description: 'Diagnostiquer l’hétéroscédasticité.', color: colors.amber, background: colors.amberSoft },
    { id: 'ols' as const, number: '07', title: 'Régression OLS', description: 'Expliquer une variable quantitative.', color: colors.teal, background: colors.tealSoft },
    { id: 'logit' as const, number: '08', title: 'Modèle Logit', description: 'Estimer la probabilité d’un événement binaire.', color: colors.coral, background: colors.coralSoft },
    { id: 'probit' as const, number: '09', title: 'Modèle Probit', description: 'Estimer une probabilité avec la loi normale.', color: colors.amber, background: colors.amberSoft },
  ];
  return <SafeAreaView style={styles.safe}><ScrollView contentContainerStyle={styles.content}><Text style={styles.kicker}>CHOISIR UNE MÉTHODE</Text><Text style={styles.title}>{datasetName}</Text><Text style={styles.subtitle}>Sélectionnez une analyse à appliquer à ce dataset.</Text>{methods.map((method) => <Pressable accessibilityRole="button" key={method.id} onPress={() => navigation.navigate('MethodAnalysis', { datasetId, datasetName, method: method.id })} style={[styles.method, { backgroundColor: method.background }]}><View style={[styles.number, { backgroundColor: method.color }]}><Text style={styles.numberText}>{method.number}</Text></View><Text style={styles.methodTitle}>{method.title}</Text><Text style={styles.description}>{method.description}</Text><Text style={[styles.action, { color: method.color }]}>Configurer l’analyse  →</Text></Pressable>)}</ScrollView></SafeAreaView>;
}

const styles = StyleSheet.create({ safe: { backgroundColor: colors.paper, flex: 1 }, content: { padding: spacing.lg }, kicker: { color: colors.coral, fontSize: 12, fontWeight: '800', letterSpacing: 1.5, marginBottom: spacing.sm }, title: { color: colors.ink, fontSize: 28, fontWeight: '800' }, subtitle: { color: colors.muted, fontSize: 15, lineHeight: 22, marginBottom: spacing.xl, marginTop: spacing.xs }, method: { borderRadius: 12, marginBottom: spacing.md, padding: spacing.lg }, number: { alignItems: 'center', borderRadius: 18, height: 36, justifyContent: 'center', marginBottom: spacing.md, width: 36 }, numberText: { color: colors.surface, fontSize: 13, fontWeight: '800' }, methodTitle: { color: colors.ink, fontSize: 20, fontWeight: '800' }, description: { color: colors.muted, fontSize: 15, lineHeight: 22, marginTop: spacing.xs }, action: { fontSize: 13, fontWeight: '800', marginTop: spacing.md } });
