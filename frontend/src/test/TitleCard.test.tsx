import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { TitleCard } from '../components/TitleCard';
import type { Title } from '../types';

const movie: Title = {
  id: 1,
  title: 'Oppenheimer',
  year: 2023,
  type: 'movie',
  rating: 8.9,
  popularity_rank: 1,
  poster_url: 'https://example.com/poster.jpg',
  overview: 'Příběh amerického fyzika J. Roberta Oppenheimera.',
  trailer_url: 'https://www.youtube.com/embed/uYPbbksJxIg',
  genres: ['Drama', 'Biografie'],
};

const series: Title = {
  id: 2,
  title: 'Stranger Things',
  year: 2016,
  type: 'series',
  rating: 8.7,
  popularity_rank: 2,
  poster_url: 'https://example.com/poster2.jpg',
  overview: 'Nadpřirozené záhady se odehrávají v malém městě Hawkins.',
  trailer_url: '',
  genres: ['Sci-Fi', 'Drama'],
};

const longOverviewTitle: Title = {
  ...movie,
  id: 3,
  overview: 'A'.repeat(120),
};

describe('TitleCard', () => {
  it('renders the title', () => {
    render(<TitleCard title={movie} onClick={vi.fn()} />);
    expect(screen.getByText('Oppenheimer')).toBeInTheDocument();
  });

  it('renders the year', () => {
    render(<TitleCard title={movie} onClick={vi.fn()} />);
    expect(screen.getByText('2023')).toBeInTheDocument();
  });

  it('shows "Film" badge for movie type', () => {
    render(<TitleCard title={movie} onClick={vi.fn()} />);
    expect(screen.getByText('Film')).toBeInTheDocument();
  });

  it('shows "Seriál" badge for series type', () => {
    render(<TitleCard title={series} onClick={vi.fn()} />);
    expect(screen.getByText('Seriál')).toBeInTheDocument();
  });

  it('renders the poster image with correct alt text', () => {
    render(<TitleCard title={movie} onClick={vi.fn()} />);
    expect(screen.getByAltText('Plakát: Oppenheimer')).toBeInTheDocument();
  });

  it('truncates overview longer than 100 characters with ellipsis', () => {
    render(<TitleCard title={longOverviewTitle} onClick={vi.fn()} />);
    const text = screen.getByText(/A+…/);
    expect(text.textContent).toHaveLength(101); // 100 chars + ellipsis char
  });

  it('does not truncate overview shorter than or equal to 100 characters', () => {
    render(<TitleCard title={movie} onClick={vi.fn()} />);
    expect(screen.getByText(movie.overview)).toBeInTheDocument();
  });

  it('calls onClick when card is clicked', async () => {
    const onClick = vi.fn();
    render(<TitleCard title={movie} onClick={onClick} />);
    await userEvent.click(screen.getByText('Oppenheimer'));
    expect(onClick).toHaveBeenCalledWith(movie);
  });

  it('calls onClick when the Detail button is clicked', async () => {
    const onClick = vi.fn();
    render(<TitleCard title={movie} onClick={onClick} />);
    await userEvent.click(screen.getByRole('button', { name: 'Zobrazit detail: Oppenheimer' }));
    expect(onClick).toHaveBeenCalledWith(movie);
  });

  it('renders the poster with lazy loading', () => {
    render(<TitleCard title={movie} onClick={vi.fn()} />);
    expect(screen.getByAltText('Plakát: Oppenheimer')).toHaveAttribute('loading', 'lazy');
  });
});
