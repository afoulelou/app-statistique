import { Platform } from 'react-native';

import type { TokenResponse, User } from './types';
import { tokenStorage } from './storage';

const configuredApiUrl = process.env.EXPO_PUBLIC_API_URL?.trim().replace(/\/+$/, '');
const browserHost = typeof window !== 'undefined' && window.location?.hostname ? window.location.hostname : '127.0.0.1';
const API_URL = configuredApiUrl || (Platform.OS === 'web' ? `http://${browserHost}:8000` : 'http://127.0.0.1:8000');
const ACCESS_TOKEN_KEY = 'app-statistique.access-token';
const REFRESH_TOKEN_KEY = 'app-statistique.refresh-token';
const REQUEST_TIMEOUT_MS = 15000;


type RegisterPayload = {
  first_name: string;
  last_name: string;
  email: string;
  password: string;
};

function errorMessage(detail: unknown): string {
  if (typeof detail === 'string' && detail.trim()) return detail;
  if (detail !== undefined && detail !== null) return JSON.stringify(detail);
  return 'Une erreur est survenue.';
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`, {
      ...options,
      signal: controller.signal,
      headers: { 'Content-Type': 'application/json', ...(options.headers ?? {}) },
    });
  } catch (caught) {
    throw new Error(caught instanceof Error && caught.name === 'AbortError' ? 'Le serveur met trop de temps à répondre.' : 'Serveur inaccessible. Vérifiez votre connexion.');
  } finally {
    clearTimeout(timeout);
  }
  if (!response.ok) {
    const body = (await response.json().catch(() => ({}))) as { detail?: unknown };
    throw new Error(errorMessage(body.detail));
  }
  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}

async function refreshAccessToken(): Promise<string> {
  const refreshToken = await tokenStorage.get(REFRESH_TOKEN_KEY);
  if (!refreshToken) throw new Error('Session expiree.');
  const tokens = await request<TokenResponse>('/auth/refresh', {
    method: 'POST',
    body: JSON.stringify({ refresh_token: refreshToken }),
  });
  await tokenStorage.set(ACCESS_TOKEN_KEY, tokens.access_token);
  await tokenStorage.set(REFRESH_TOKEN_KEY, tokens.refresh_token);
  return tokens.access_token;
}

export async function authenticatedRequest<T>(path: string, options: RequestInit = {}): Promise<T> {
  let token = await tokenStorage.get(ACCESS_TOKEN_KEY);
  if (!token) throw new Error('Session absente.');
  const send = async (accessToken: string): Promise<Response> => {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
    try {
      return await fetch(`${API_URL}${path}`, {
        ...options,
        signal: controller.signal,
        headers: { ...(options.headers ?? {}), Authorization: `Bearer ${accessToken}` },
      });
    } catch (caught) {
      throw new Error(caught instanceof Error && caught.name === 'AbortError' ? 'Le serveur met trop de temps à répondre.' : 'Serveur inaccessible. Vérifiez votre connexion.');
    } finally {
      clearTimeout(timeout);
    }
  };
  let response: Response;
  try {
    response = await send(token);
  } catch {
    throw new Error('Serveur inaccessible. Vérifiez votre connexion.');
  }
  if (response.status === 401) {
    try {
      token = await refreshAccessToken();
      response = await send(token);
    } catch (caught) {
      await tokenStorage.delete(ACCESS_TOKEN_KEY);
      await tokenStorage.delete(REFRESH_TOKEN_KEY);
      throw caught instanceof Error ? caught : new Error('Session expirée.');
    }
  }
  if (!response.ok) {
    const body = (await response.json().catch(() => ({}))) as { detail?: unknown };
    throw new Error(errorMessage(body.detail));
  }
  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}

export async function login(email: string, password: string): Promise<User> {
  const tokens = await request<TokenResponse>('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
  await tokenStorage.set(ACCESS_TOKEN_KEY, tokens.access_token);
  await tokenStorage.set(REFRESH_TOKEN_KEY, tokens.refresh_token);
  return getCurrentUser();
}

export async function register(payload: RegisterPayload): Promise<void> {
  await request<User>('/auth/register', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function getCurrentUser(): Promise<User> {
  const token = await tokenStorage.get(ACCESS_TOKEN_KEY);
  if (!token) {
    throw new Error('Session absente.');
  }
  return authenticatedRequest<User>('/users/me');
}

export async function logout(): Promise<void> {
  const refreshToken = await tokenStorage.get(REFRESH_TOKEN_KEY);
  if (refreshToken) {
    await request<void>('/auth/logout', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: refreshToken }),
    }).catch(() => undefined);
  }
  await tokenStorage.delete(ACCESS_TOKEN_KEY);
  await tokenStorage.delete(REFRESH_TOKEN_KEY);
}
