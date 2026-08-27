import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { SafeAreaView, ScrollView, StyleSheet, Text, View } from 'react-native';
import { useState } from 'react';

import { useAuth } from '../auth';
import { FormField } from '../components/FormField';
import { PrimaryButton } from '../components/PrimaryButton';
import { colors, spacing } from '../theme';
import type { RootStackParamList } from '../types';

type Props = NativeStackScreenProps<RootStackParamList, 'Register'>;

export function RegisterScreen({ navigation }: Props) {
  const { signUp } = useAuth();
  const [firstName, setFirstName] = useState(''); const [lastName, setLastName] = useState(''); const [email, setEmail] = useState(''); const [password, setPassword] = useState(''); const [error, setError] = useState(''); const [loading, setLoading] = useState(false);
  async function submit() { setError(''); setLoading(true); try { await signUp(firstName, lastName, email, password); } catch (caught) { setError(caught instanceof Error ? caught.message : 'Inscription impossible.'); } finally { setLoading(false); } }
  return <SafeAreaView style={styles.safe}><ScrollView contentContainerStyle={styles.content}><Text style={styles.kicker}>PREMIÈRE ÉTAPE</Text><Text style={styles.title}>Créez votre espace de travail.</Text><Text style={styles.subtitle}>Un compte pour retrouver vos datasets et vos analyses.</Text><View style={styles.form}><FormField label="Prénom" onChangeText={setFirstName} placeholder="Awa" value={firstName} /><FormField label="Nom" onChangeText={setLastName} placeholder="Diallo" value={lastName} /><FormField autoCapitalize="none" label="Adresse e-mail" onChangeText={setEmail} placeholder="vous@exemple.com" value={email} /><FormField label="Mot de passe" onChangeText={setPassword} placeholder="8 caractères minimum" secureTextEntry value={password} />{error ? <Text style={styles.error}>{error}</Text> : null}<PrimaryButton label="Créer mon compte" loading={loading} onPress={submit} /></View><Text onPress={() => navigation.goBack()} style={styles.link}>J’ai déjà un compte</Text></ScrollView></SafeAreaView>;
}

const styles = StyleSheet.create({ safe: { backgroundColor: colors.paper, flex: 1 }, content: { flexGrow: 1, justifyContent: 'center', padding: spacing.lg }, kicker: { color: colors.coral, fontSize: 12, fontWeight: '800', letterSpacing: 1.5, marginBottom: spacing.sm }, title: { color: colors.ink, fontSize: 32, fontWeight: '800', lineHeight: 38 }, subtitle: { color: colors.muted, fontSize: 16, lineHeight: 24, marginBottom: spacing.xl, marginTop: spacing.md }, form: { backgroundColor: colors.surface, borderColor: colors.line, borderRadius: 12, borderWidth: 1, gap: spacing.md, padding: spacing.lg }, error: { color: colors.danger, fontSize: 14 }, link: { color: colors.teal, fontSize: 15, fontWeight: '700', marginTop: spacing.lg, textAlign: 'center' } });
