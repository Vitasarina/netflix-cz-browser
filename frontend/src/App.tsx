import { useState, useEffect, useCallback } from 'react';
import type { Title, FilterType } from './types';
import { fetchTrending } from './api';
import { MOCK_TITLES } from './mockData';
import { FilterTabs } from './components/FilterTabs';
import { TitleCard } from './components/TitleCard';
import { SkeletonCard } from './components/SkeletonCard';
import { DetailModal } from './components/DetailModal';
import './index.css';

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';

export default function App() {
  const [titles, setTitles] = useState<Title[]>([]);
  const [filter, setFilter] = useState<FilterType>('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<Title | null>(null);

  const load = useCallback(async (f: FilterType) => {
    setLoading(true);
    setError(null);
    try {
      if (USE_MOCK) {
        await new Promise((r) => setTimeout(r, 600)); // simulate latency
        const filtered = f === 'all' ? MOCK_TITLES : MOCK_TITLES.filter((t) => t.type === f);
        setTitles(filtered);
      } else {
        const data = await fetchTrending(f);
        setTitles(data);
      }
    } catch {
      setError('Nepodařilo se načíst trendy. Zkontrolujte připojení a zkuste znovu.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load(filter);
  }, [filter, load]);

  function handleFilterChange(f: FilterType) {
    setFilter(f);
  }

  return (
    <div className="min-h-screen bg-[#141414]">
      {/* Header */}
      <header className="sticky top-0 z-30 bg-[#141414]/95 backdrop-blur-sm border-b border-[#2f2f2f]">
        <div className="max-w-screen-xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between gap-4 flex-wrap">
          <div className="flex items-center gap-2">
            <span className="text-[#E50914] font-black text-2xl tracking-tighter select-none">CZ</span>
            <span className="text-white font-bold text-xl tracking-wide select-none">TRENDING</span>
          </div>
          <FilterTabs active={filter} onChange={handleFilterChange} />
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-screen-xl mx-auto px-4 sm:px-6 py-8">
        {/* Heading */}
        <h1 className="text-white text-2xl sm:text-3xl font-bold mb-6">
          {filter === 'all' && 'Nejsledovanější na Netflixu CZ'}
          {filter === 'movie' && 'Nejsledovanější filmy'}
          {filter === 'series' && 'Nejsledovanější seriály'}
        </h1>

        {/* Error state */}
        {error && !loading && (
          <div className="flex flex-col items-center justify-center py-20 text-center gap-4">
            <div className="text-5xl">⚠️</div>
            <p className="text-[#8c8c8c] text-lg max-w-md">{error}</p>
            <button
              className="bg-[#E50914] hover:bg-[#f40612] text-white font-semibold px-6 py-2 rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-white"
              onClick={() => load(filter)}
            >
              Zkusit znovu
            </button>
          </div>
        )}

        {/* Grid */}
        {!error && (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
            {loading
              ? Array.from({ length: 10 }).map((_, i) => <SkeletonCard key={i} />)
              : titles.map((t) => (
                  <TitleCard key={t.id} title={t} onClick={setSelected} />
                ))}
          </div>
        )}

        {/* Empty state */}
        {!loading && !error && titles.length === 0 && (
          <div className="text-center py-20 text-[#8c8c8c]">
            Žádné výsledky pro vybraný filtr.
          </div>
        )}
      </main>

      {/* Detail modal */}
      {selected && (
        <DetailModal title={selected} onClose={() => setSelected(null)} />
      )}
    </div>
  );
}
