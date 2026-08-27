import AsyncStorage from '@react-native-async-storage/async-storage';

export const tokenStorage = {
  get: (key: string) => AsyncStorage.getItem(key),
  set: (key: string, value: string) => AsyncStorage.setItem(key, value),
  delete: (key: string) => AsyncStorage.removeItem(key),
};
