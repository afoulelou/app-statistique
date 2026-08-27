import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { KeyboardAvoidingView, Platform, Pressable, SafeAreaView, ScrollView, StyleSheet, Text, View } from 'react-native';
import { useState } from 'react';

import { useAuth } from '../auth';
import { FormField } from '../components/FormField';
import { PrimaryButton } from '../components/PrimaryButton';
import { colors, spacing } from '../theme';
import type { RootStackParamList } from '../types';

type Props = NativeStackScreenProps<RootStackParamList, 'Login'>;

export function LoginScreen({ navigation }: Props) {
  const { signIn } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function submit() {
    setError('');
    setLoading(true);
    try { await signIn(email, password); } catch (caught) { setError(caught instanceof Error ? caught.message : 'Connexion impossible.'); } finally { setLoading(false); }
  }

  return <SafeAreaView style={styles.safe}><KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : undefined} style={styles.keyboard}><ScrollView contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled"><View style={styles.brand}><Text style={styles.kicker}>APP STATISTIQUE</Text><Text style={styles.title}>Comprendre les données. Décider avec méthode.</Text><Text style={styles.subtitle}>Votre espace d’apprentissage et d’analyse, au même endroit.</Text></View><View style={styles.form}><Text style={styles.heading}>Connexion</Text><FormField autoCapitalize="none" label="Adresse e-mail" onChangeText={setEmail} placeholder="vous@exemple.com" value={email} /><FormField label="Mot de passe" onChangeText={setPassword} placeholder="Votre mot de passe" secureTextEntry value={password} />{error ? <Text style={styles.error}>{error}</Text> : null}<PrimaryButton label="Se connecter" loading={loading} onPress={submit} /><Pressable accessibilityRole="button" onPress={() => navigation.navigate('Register')}><Text style={styles.link}>Créer un compte</Text></Pressable></View></ScrollView></KeyboardAvoidingView></SafeAreaView>;
}

const styles = StyleSheet.create({ safe: { backgroundColor: colors.paper, flex: 1 }, keyboard: { flex: 1 }, content: { flexGrow: 1, justifyContent: 'center', padding: spacing.lg }, brand: { marginBottom: spacing.xl }, kicker: { color: colors.coral, fontSize: 12, fontWeight: '800', letterSpacing: 1.5, marginBottom: spacing.sm }, title: { color: colors.ink, fontSize: 32, fontWeight: '800', lineHeight: 38 }, subtitle: { color: colors.muted, fontSize: 16, lineHeight: 24, marginTop: spacing.md }, form: { backgroundColor: colors.surface, borderColor: colors.line, borderRadius: 12, borderWidth: 1, gap: spacing.md, padding: spacing.lg }, heading: { color: colors.ink, fontSize: 24, fontWeight: '800' }, error: { color: colors.danger, fontSize: 14, lineHeight: 20 }, link: { color: colors.teal, fontSize: 15, fontWeight: '700', paddingVertical: spacing.xs, textAlign: 'center' } });
