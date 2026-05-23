import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { FilterTabs } from '../components/FilterTabs';

describe('FilterTabs', () => {
  it('renders all three tabs', () => {
    render(<FilterTabs active="all" onChange={vi.fn()} />);
    expect(screen.getByRole('tab', { name: 'Vše' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: 'Filmy' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: 'Seriály' })).toBeInTheDocument();
  });

  it('marks the active tab with aria-selected=true', () => {
    render(<FilterTabs active="movie" onChange={vi.fn()} />);
    expect(screen.getByRole('tab', { name: 'Filmy' })).toHaveAttribute('aria-selected', 'true');
    expect(screen.getByRole('tab', { name: 'Vše' })).toHaveAttribute('aria-selected', 'false');
    expect(screen.getByRole('tab', { name: 'Seriály' })).toHaveAttribute('aria-selected', 'false');
  });

  it('calls onChange with the correct value when a tab is clicked', async () => {
    const onChange = vi.fn();
    render(<FilterTabs active="all" onChange={onChange} />);
    await userEvent.click(screen.getByRole('tab', { name: 'Filmy' }));
    expect(onChange).toHaveBeenCalledWith('movie');
  });

  it('calls onChange with "series" when Seriály tab is clicked', async () => {
    const onChange = vi.fn();
    render(<FilterTabs active="all" onChange={onChange} />);
    await userEvent.click(screen.getByRole('tab', { name: 'Seriály' }));
    expect(onChange).toHaveBeenCalledWith('series');
  });

  it('calls onChange with "all" when Vše tab is clicked', async () => {
    const onChange = vi.fn();
    render(<FilterTabs active="movie" onChange={onChange} />);
    await userEvent.click(screen.getByRole('tab', { name: 'Vše' }));
    expect(onChange).toHaveBeenCalledWith('all');
  });

  it('renders the tablist with an accessible label', () => {
    render(<FilterTabs active="all" onChange={vi.fn()} />);
    expect(screen.getByRole('tablist', { name: 'Filtrovat tituly' })).toBeInTheDocument();
  });
});
