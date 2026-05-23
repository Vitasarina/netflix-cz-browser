import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import App from '../App';
import * as api from '../api';
import type { Title } from '../types';

vi.mock('../api');

const movieTitle: Title = {
  id: 1,
  title: 'Oppenheimer',
  year: 2023,
  type: 'movie',
  rating: 8.9,
  popularity_rank: 1,
  poster_url: 'https://example.com/poster.jpg',
  overview: 'Test overview for Oppenheimer.',
  trailer_url: '',
  genres: ['Drama'],
};

const seriesTitle: Title = {
  id: 2,
  title: 'Stranger Things',
  year: 2016,
  type: 'series',
  rating: 8.7,
  popularity_rank: 2,
  poster_url: 'https://example.com/poster2.jpg',
  overview: 'Test overview for Stranger Things.',
  trailer_url: '',
  genres: ['Sci-Fi'],
};

beforeEach(() => {
  vi.mocked(api.fetchTrending).mockResolvedValue([movieTitle, seriesTitle]);
});

describe('App', () => {
  it('shows skeleton cards while loading', () => {
    vi.mocked(api.fetchTrending).mockReturnValue(new Promise(() => {}));
    render(<App />);
    const skeletons = document.querySelectorAll('.animate-pulse');
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it('renders title cards after successful fetch', async () => {
    render(<App />);
    await waitFor(() => {
      expect(screen.getByText('Oppenheimer')).toBeInTheDocument();
      expect(screen.getByText('Stranger Things')).toBeInTheDocument();
    });
  });

  it('shows error state when fetch fails', async () => {
    vi.mocked(api.fetchTrending).mockRejectedValue(new Error('Network error'));
    render(<App />);
    await waitFor(() => {
      expect(screen.getByText(/Nepodařilo se načíst trendy/)).toBeInTheDocument();
    });
  });

  it('shows a retry button in error state', async () => {
    vi.mocked(api.fetchTrending).mockRejectedValue(new Error('Network error'));
    render(<App />);
    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'Zkusit znovu' })).toBeInTheDocument();
    });
  });

  it('retries fetch when retry button is clicked', async () => {
    vi.mocked(api.fetchTrending)
      .mockRejectedValueOnce(new Error('Network error'))
      .mockResolvedValue([movieTitle]);
    render(<App />);
    await waitFor(() => screen.getByRole('button', { name: 'Zkusit znovu' }));
    await userEvent.click(screen.getByRole('button', { name: 'Zkusit znovu' }));
    await waitFor(() => {
      expect(screen.getByText('Oppenheimer')).toBeInTheDocument();
    });
  });

  it('shows "Vše" heading by default', async () => {
    render(<App />);
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Nejsledovanější na Netflixu CZ' })).toBeInTheDocument();
    });
  });

  it('changes heading when "Filmy" filter is selected', async () => {
    render(<App />);
    await waitFor(() => screen.getByText('Oppenheimer'));
    await userEvent.click(screen.getByRole('tab', { name: 'Filmy' }));
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Nejsledovanější filmy' })).toBeInTheDocument();
    });
  });

  it('changes heading when "Seriály" filter is selected', async () => {
    render(<App />);
    await waitFor(() => screen.getByText('Oppenheimer'));
    await userEvent.click(screen.getByRole('tab', { name: 'Seriály' }));
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Nejsledovanější seriály' })).toBeInTheDocument();
    });
  });

  it('calls fetchTrending with "movie" when Filmy tab is clicked', async () => {
    render(<App />);
    await waitFor(() => screen.getByText('Oppenheimer'));
    await userEvent.click(screen.getByRole('tab', { name: 'Filmy' }));
    await waitFor(() => {
      expect(api.fetchTrending).toHaveBeenCalledWith('movie');
    });
  });

  it('opens detail modal when a title card is clicked', async () => {
    render(<App />);
    await waitFor(() => screen.getByText('Oppenheimer'));
    await userEvent.click(screen.getByText('Oppenheimer'));
    expect(screen.getByRole('dialog')).toBeInTheDocument();
  });

  it('closes the detail modal when close button is clicked', async () => {
    render(<App />);
    await waitFor(() => screen.getByText('Oppenheimer'));
    await userEvent.click(screen.getByText('Oppenheimer'));
    await userEvent.click(screen.getByRole('button', { name: 'Zavřít' }));
    await waitFor(() => {
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    });
  });

  it('shows empty state when titles array is empty', async () => {
    vi.mocked(api.fetchTrending).mockResolvedValue([]);
    render(<App />);
    await waitFor(() => {
      expect(screen.getByText('Žádné výsledky pro vybraný filtr.')).toBeInTheDocument();
    });
  });

  it('renders filter tabs in header', async () => {
    render(<App />);
    expect(screen.getByRole('tablist')).toBeInTheDocument();
  });
});
