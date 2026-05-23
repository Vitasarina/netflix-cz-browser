import type { FilterType } from '../types';

interface Props {
  active: FilterType;
  onChange: (f: FilterType) => void;
}

const TABS: { label: string; value: FilterType }[] = [
  { label: 'Vše', value: 'all' },
  { label: 'Filmy', value: 'movie' },
  { label: 'Seriály', value: 'series' },
];

export function FilterTabs({ active, onChange }: Props) {
  return (
    <div className="flex gap-2" role="tablist" aria-label="Filtrovat tituly">
      {TABS.map((tab) => (
        <button
          key={tab.value}
          role="tab"
          aria-selected={active === tab.value}
          className={`px-4 py-2 rounded-full text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-[#E50914] ${
            active === tab.value
              ? 'bg-[#E50914] text-white'
              : 'bg-[#2f2f2f] text-[#8c8c8c] hover:bg-[#3a3a3a] hover:text-white'
          }`}
          onClick={() => onChange(tab.value)}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
}
