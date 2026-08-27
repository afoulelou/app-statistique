import { createContext, useContext, useEffect, useState } from 'react';

import * as api from './api';
import type { User } from './types';

type AuthContextValue = {
  user: User | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (firstName: string, lastName: string, email: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getCurrentUser().then(setUser).catch(() => undefined).finally(() => setLoading(false));
  }, []);

  async function signIn(email: string, password: string) {
    setUser(await api.login(email, password));
  }

  async function signUp(firstName: string, lastName: string, email: string, password: string) {
    await api.register({ first_name: firstName, last_name: lastName, email, password });
    setUser(await api.login(email, password));
  }

  async function signOut() {
    await api.logout();
    setUser(null);
  }

  return <AuthContext.Provider value={{ user, loading, signIn, signUp, signOut }}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth doit etre utilise dans AuthProvider.');
  return context;
}
