import { useEffect, useRef } from 'react';
import type { Title } from '../types';

interface Props {
  title: Title;
  onClose: () => void;
}

export function DetailModal({ title, onClose }: Props) {
  const overlayRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key === 'Escape') onClose();
    }
    document.addEventListener('keydown', onKey);
    document.body.style.overflow = 'hidden';
    return () => {
      document.removeEventListener('keydown', onKey);
      document.body.style.overflow = '';
    };
  }, [onClose]);

  function handleOverlayClick(e: React.MouseEvent) {
    if (e.target === overlayRef.current) onClose();
  }

  const trailerSrc = title.trailer_url
    ? title.trailer_url.includes('?')
      ? title.trailer_url + '&autoplay=0'
      : title.trailer_url + '?autoplay=0'
    : null;

  return (
    <div
      ref={overlayRef}
      className="fixed inset-0 z-50 bg-black/80 flex items-center justify-center p-4"
      onClick={handleOverlayClick}
      role="dialog"
      aria-modal="true"
      aria-label={title.title}
    >
      <div className="bg-[#1a1a1a] rounded-lg w-full max-w-3xl max-h-[90vh] overflow-y-auto relative">
        {/* Close button */}
        <button
          className="absolute top-3 right-3 z-10 w-9 h-9 flex items-center justify-center rounded-full bg-black/60 hover:bg-black text-white text-xl leading-none transition-colors focus:outline-none focus:ring-2 focus:ring-[#E50914]"
          onClick={onClose}
          aria-label="Zavřít"
        >
          ✕
        </button>

        {/* Trailer */}
        {trailerSrc && (
          <div className="aspect-video w-full bg-black rounded-t-lg overflow-hidden">
            <iframe
              src={trailerSrc}
              title={`Trailer: ${title.title}`}
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
              className="w-full h-full"
            />
          </div>
        )}

        {/* Content */}
        <div className="p-6">
          <div className="flex flex-wrap items-center gap-3 mb-3">
            <h2 className="text-white text-2xl font-bold leading-tight">{title.title}</h2>
            <span className={`text-xs font-bold px-2 py-1 rounded uppercase tracking-wide ${
              title.type === 'movie'
                ? 'bg-[#E50914] text-white'
                : 'bg-blue-600 text-white'
            }`}>
              {title.type === 'movie' ? 'Film' : 'Seriál'}
            </span>
          </div>

          <div className="flex flex-wrap items-center gap-4 text-sm text-[#8c8c8c] mb-4">
            <span>{title.year}</span>
            <span className="flex items-center gap-1">
              <span className="text-yellow-400">★</span>
              <span className="text-white font-semibold">{title.rating.toFixed(1)}</span>
              <span>/10</span>
            </span>
            <span>#{title.popularity_rank} trending</span>
          </div>

          {title.genres.length > 0 && (
            <div className="flex flex-wrap gap-2 mb-4">
              {title.genres.map((g) => (
                <span
                  key={g}
                  className="bg-[#2f2f2f] text-[#8c8c8c] text-xs px-2 py-1 rounded"
                >
                  {g}
                </span>
              ))}
            </div>
          )}

          <p className="text-[#cccccc] text-sm leading-relaxed">{title.overview}</p>
        </div>
      </div>
    </div>
  );
}
