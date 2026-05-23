import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { fetchTrending } from '../api';
import type { Title } from '../types';

const mockTitles: Title[] = [
  {
    id: 1,
    title: 'Oppenheimer',
    year: 2023,
    type: 'movie',
    rating: 8.9,
    popularity_rank: 1,
    poster_url: 'https://example.com/poster.jpg',
    overview: 'Test overview.',
    trailer_url: '',
    genres: ['Drama'],
  },
];

beforeEach(() => {
  vi.stubGlobal('fetch', vi.fn());
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe('fetchTrending', () => {
  it('fetches from /api/trending without type filter when type is "all"', async () => {
    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      json: async () => mockTitles,
    } as Response);

    await fetchTrending('all');
    expect(fetch).toHaveBeenCalledWith('http://localhost:8000/api/trending');
  });

  it('fetches from /api/trending without query param when type is undefined', async () => {
    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      json: async () => mockTitles,
    } as Response);

    await fetchTrending();
    expect(fetch).toHaveBeenCalledWith('http://localhost:8000/api/trending');
  });

  it('appends type=movie query param when type is "movie"', async () => {
    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      json: async () => mockTitles,
    } as Response);

    await fetchTrending('movie');
    expect(fetch).toHaveBeenCalledWith('http://localhost:8000/api/trending?type=movie');
  });

  it('appends type=series query param when type is "series"', async () => {
    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      json: async () => mockTitles,
    } as Response);

    await fetchTrending('series');
    expect(fetch).toHaveBeenCalledWith('http://localhost:8000/api/trending?type=series');
  });

  it('returns the parsed JSON data on success', async () => {
    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      json: async () => mockTitles,
    } as Response);

    const result = await fetchTrending();
    expect(result).toEqual(mockTitles);
  });

  it('throws an error when response is not ok (404)', async () => {
    vi.mocked(fetch).mockResolvedValue({
      ok: false,
      status: 404,
    } as Response);

    await expect(fetchTrending()).rejects.toThrow('API error 404');
  });

  it('throws an error when response is not ok (500)', async () => {
    vi.mocked(fetch).mockResolvedValue({
      ok: false,
      status: 500,
    } as Response);

    await expect(fetchTrending()).rejects.toThrow('API error 500');
  });

  it('propagates network errors (fetch rejects)', async () => {
    vi.mocked(fetch).mockRejectedValue(new Error('Network error'));

    await expect(fetchTrending()).rejects.toThrow('Network error');
  });
});
