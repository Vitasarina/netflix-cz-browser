import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, afterEach } from 'vitest';
import { DetailModal } from '../components/DetailModal';
import type { Title } from '../types';

const titleWithTrailer: Title = {
  id: 1,
  title: 'Oppenheimer',
  year: 2023,
  type: 'movie',
  rating: 8.9,
  popularity_rank: 1,
  poster_url: 'https://example.com/poster.jpg',
  overview: 'Příběh amerického fyzika J. Roberta Oppenheimera.',
  trailer_url: 'https://www.youtube.com/embed/uYPbbksJxIg',
  genres: ['Drama', 'Biografie', 'Historie'],
};

const titleNoTrailer: Title = {
  ...titleWithTrailer,
  id: 2,
  title: 'Bez traileru',
  trailer_url: '',
};

const seriesTitle: Title = {
  ...titleWithTrailer,
  id: 3,
  title: 'Stranger Things',
  type: 'series',
  genres: [],
};

afterEach(() => {
  document.body.style.overflow = '';
});

describe('DetailModal', () => {
  it('renders the movie title', () => {
    render(<DetailModal title={titleWithTrailer} onClose={vi.fn()} />);
    expect(screen.getByRole('heading', { name: 'Oppenheimer' })).toBeInTheDocument();
  });

  it('renders the dialog with correct aria-label', () => {
    render(<DetailModal title={titleWithTrailer} onClose={vi.fn()} />);
    expect(screen.getByRole('dialog', { name: 'Oppenheimer' })).toBeInTheDocument();
  });

  it('renders year, rating, and popularity rank', () => {
    render(<DetailModal title={titleWithTrailer} onClose={vi.fn()} />);
    expect(screen.getByText('2023')).toBeInTheDocument();
    expect(screen.getByText('8.9')).toBeInTheDocument();
    expect(screen.getByText('#1 trending')).toBeInTheDocument();
  });

  it('renders genres as tags', () => {
    render(<DetailModal title={titleWithTrailer} onClose={vi.fn()} />);
    expect(screen.getByText('Drama')).toBeInTheDocument();
    expect(screen.getByText('Biografie')).toBeInTheDocument();
    expect(screen.getByText('Historie')).toBeInTheDocument();
  });

  it('does not render genre tags when genres array is empty', () => {
    render(<DetailModal title={seriesTitle} onClose={vi.fn()} />);
    expect(screen.queryByText('Drama')).not.toBeInTheDocument();
  });

  it('renders the overview text', () => {
    render(<DetailModal title={titleWithTrailer} onClose={vi.fn()} />);
    expect(screen.getByText(titleWithTrailer.overview)).toBeInTheDocument();
  });

  it('shows "Film" badge for movie', () => {
    render(<DetailModal title={titleWithTrailer} onClose={vi.fn()} />);
    expect(screen.getByText('Film')).toBeInTheDocument();
  });

  it('shows "Seriál" badge for series', () => {
    render(<DetailModal title={seriesTitle} onClose={vi.fn()} />);
    expect(screen.getByText('Seriál')).toBeInTheDocument();
  });

  it('renders the trailer iframe when trailer_url is set', () => {
    render(<DetailModal title={titleWithTrailer} onClose={vi.fn()} />);
    const iframe = screen.getByTitle('Trailer: Oppenheimer');
    expect(iframe).toBeInTheDocument();
    expect(iframe).toHaveAttribute('src', 'https://www.youtube.com/embed/uYPbbksJxIg?autoplay=0');
  });

  it('appends autoplay=0 with & when trailer_url already has query params', () => {
    const t = { ...titleWithTrailer, trailer_url: 'https://example.com/embed/x?rel=0' };
    render(<DetailModal title={t} onClose={vi.fn()} />);
    const iframe = screen.getByTitle(`Trailer: ${t.title}`);
    expect(iframe).toHaveAttribute('src', 'https://example.com/embed/x?rel=0&autoplay=0');
  });

  it('does not render iframe when trailer_url is empty', () => {
    render(<DetailModal title={titleNoTrailer} onClose={vi.fn()} />);
    expect(screen.queryByTitle(/Trailer/)).not.toBeInTheDocument();
  });

  it('calls onClose when close button is clicked', async () => {
    const onClose = vi.fn();
    render(<DetailModal title={titleWithTrailer} onClose={onClose} />);
    await userEvent.click(screen.getByRole('button', { name: 'Zavřít' }));
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('calls onClose when Escape key is pressed', async () => {
    const onClose = vi.fn();
    render(<DetailModal title={titleWithTrailer} onClose={onClose} />);
    await userEvent.keyboard('{Escape}');
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('locks body scroll when mounted and restores it on unmount', () => {
    const { unmount } = render(<DetailModal title={titleWithTrailer} onClose={vi.fn()} />);
    expect(document.body.style.overflow).toBe('hidden');
    unmount();
    expect(document.body.style.overflow).toBe('');
  });

  it('calls onClose when overlay background is clicked', async () => {
    const onClose = vi.fn();
    render(<DetailModal title={titleWithTrailer} onClose={onClose} />);
    const dialog = screen.getByRole('dialog');
    await userEvent.click(dialog);
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('does not call onClose when modal content is clicked', async () => {
    const onClose = vi.fn();
    render(<DetailModal title={titleWithTrailer} onClose={onClose} />);
    await userEvent.click(screen.getByText(titleWithTrailer.overview));
    expect(onClose).not.toHaveBeenCalled();
  });
});
