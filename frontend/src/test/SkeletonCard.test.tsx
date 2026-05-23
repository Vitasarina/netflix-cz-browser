import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { SkeletonCard } from '../components/SkeletonCard';

describe('SkeletonCard', () => {
  it('renders without crashing', () => {
    const { container } = render(<SkeletonCard />);
    expect(container.firstChild).toBeInTheDocument();
  });

  it('renders a div element', () => {
    const { container } = render(<SkeletonCard />);
    expect(container.querySelector('div')).toBeInTheDocument();
  });
});
