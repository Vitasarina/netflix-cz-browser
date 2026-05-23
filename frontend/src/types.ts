export interface Title {
  id: number;
  title: string;
  year: number;
  type: 'movie' | 'series';
  rating: number;
  popularity_rank: number;
  poster_url: string;
  overview: string;
  trailer_url: string;
  genres: string[];
}

export type FilterType = 'all' | 'movie' | 'series';
