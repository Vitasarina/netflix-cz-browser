import type { FilterType, Title } from './types';

const BASE_URL = (import.meta.env.VITE_API_URL ?? 'http://localhost:8000') + '/api';

export async function fetchTrending(type?: FilterType): Promise<Title[]> {
  const url = type && type !== 'all'
    ? `${BASE_URL}/trending?type=${type}`
    : `${BASE_URL}/trending`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}
