import { StyleSheet, Text, TextInput, View } from 'react-native';

import { colors, spacing } from '../theme';

export function FormField({ label, value, onChangeText, placeholder, secureTextEntry = false, autoCapitalize = 'sentences' }: { label: string; value: string; onChangeText: (value: string) => void; placeholder: string; secureTextEntry?: boolean; autoCapitalize?: 'none' | 'sentences' }) {
  return (
    <View style={styles.wrapper}>
      <Text style={styles.label}>{label}</Text>
      <TextInput autoCapitalize={autoCapitalize} placeholder={placeholder} placeholderTextColor={colors.muted} secureTextEntry={secureTextEntry} style={styles.input} value={value} onChangeText={onChangeText} />
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: { gap: spacing.xs },
  label: { color: colors.ink, fontSize: 14, fontWeight: '700' },
  input: { backgroundColor: colors.surface, borderColor: colors.line, borderRadius: 8, borderWidth: 1, color: colors.ink, fontSize: 16, minHeight: 52, paddingHorizontal: spacing.md },
});
