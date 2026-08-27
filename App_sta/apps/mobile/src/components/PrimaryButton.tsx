import { ActivityIndicator, Pressable, StyleSheet, Text } from 'react-native';

import { colors, spacing } from '../theme';

export function PrimaryButton({ label, onPress, loading = false }: { label: string; onPress: () => void; loading?: boolean }) {
  return (
    <Pressable accessibilityRole="button" disabled={loading} onPress={onPress} style={({ pressed }) => [styles.button, pressed && styles.pressed]}>
      {loading ? <ActivityIndicator color={colors.surface} /> : <Text style={styles.label}>{label}</Text>}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  button: { alignItems: 'center', backgroundColor: colors.teal, borderRadius: 8, minHeight: 52, justifyContent: 'center', paddingHorizontal: spacing.md },
  pressed: { opacity: 0.82 },
  label: { color: colors.surface, fontSize: 16, fontWeight: '700' },
});
