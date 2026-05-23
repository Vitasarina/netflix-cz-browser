import type { Title } from '../types';

interface Props {
  title: Title;
  onClick: (title: Title) => void;
}

export function TitleCard({ title, onClick }: Props) {
  const truncated = title.overview.length > 100
    ? title.overview.slice(0, 100) + '…'
    : title.overview;

  return (
    <div
      className="relative rounded-md overflow-hidden cursor-pointer group bg-[#1a1a1a] transition-transform duration-200 ease-out hover:scale-105 hover:z-10 focus-within:scale-105 focus-within:z-10"
      onClick={() => onClick(title)}
    >
      {/* Poster */}
      <div className="aspect-[2/3] relative overflow-hidden bg-[#2f2f2f]">
        <img
          src={title.poster_url}
          alt={`Plakát: ${title.title}`}
          className="w-full h-full object-cover"
          loading="lazy"
        />
        {/* Hover overlay */}
        <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity duration-200 flex items-center justify-center">
          <button
            className="bg-[#E50914] hover:bg-[#f40612] text-white font-semibold px-5 py-2 rounded-full text-sm transition-colors focus:outline-none focus:ring-2 focus:ring-white"
            onClick={(e) => { e.stopPropagation(); onClick(title); }}
            aria-label={`Zobrazit detail: ${title.title}`}
          >
            Detail
          </button>
        </div>
      </div>

      {/* Info */}
      <div className="p-3">
        <div className="flex items-start justify-between gap-2 mb-1">
          <h3 className="text-white font-semibold text-sm leading-tight line-clamp-2 flex-1">
            {title.title}
          </h3>
          <span className={`shrink-0 text-xs font-bold px-1.5 py-0.5 rounded uppercase tracking-wide ${
            title.type === 'movie'
              ? 'bg-[#E50914] text-white'
              : 'bg-blue-600 text-white'
          }`}>
            {title.type === 'movie' ? 'Film' : 'Seriál'}
          </span>
        </div>
        <p className="text-[#8c8c8c] text-xs mb-2">{title.year}</p>
        <p className="text-[#8c8c8c] text-xs leading-relaxed line-clamp-3">{truncated}</p>
      </div>
    </div>
  );
}
