import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';

import { AuthProvider, useAuth } from './src/auth';
import { DashboardScreen } from './src/screens/DashboardScreen';
import { DatasetScreen } from './src/screens/DatasetScreen';
import { AnalysisScreen } from './src/screens/AnalysisScreen';
import { MethodsScreen } from './src/screens/MethodsScreen';
import { MethodAnalysisScreen } from './src/screens/MethodAnalysisScreen';
import { LearningScreen } from './src/screens/LearningScreen';
import { HistoryScreen } from './src/screens/HistoryScreen';
import { LoginScreen } from './src/screens/LoginScreen';
import { RegisterScreen } from './src/screens/RegisterScreen';
import type { RootStackParamList } from './src/types';

const Stack = createNativeStackNavigator<RootStackParamList>();

function AppNavigation() {
  const { user } = useAuth();
  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        {user ? (
          <>
            <Stack.Screen name="Dashboard" component={DashboardScreen} />
            <Stack.Screen name="Dataset" component={DatasetScreen} options={{ headerShown: true, title: 'Dataset' }} />
            <Stack.Screen name="Analysis" component={AnalysisScreen} options={{ headerShown: true, title: 'Analyse' }} />
            <Stack.Screen name="Methods" component={MethodsScreen} options={{ headerShown: true, title: 'Méthodes' }} />
            <Stack.Screen name="MethodAnalysis" component={MethodAnalysisScreen} options={{ headerShown: true, title: 'Configurer' }} />
            <Stack.Screen name="Learning" component={LearningScreen} options={{ headerShown: true, title: 'Apprentissage' }} />
            <Stack.Screen name="History" component={HistoryScreen} options={{ headerShown: true, title: 'Historique' }} />
          </>
        ) : (
          <>
            <Stack.Screen name="Login" component={LoginScreen} />
            <Stack.Screen name="Register" component={RegisterScreen} />
          </>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppNavigation />
    </AuthProvider>
  );
}
