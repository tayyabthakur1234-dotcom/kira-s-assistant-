import React from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { ExternalLink, X, Globe, Search } from 'lucide-react';
import { OpenedWebsite, ThemeMode } from '../types';
import { THEMES } from '../lib/theme';

interface WebsiteOverlayProps {
  sites: OpenedWebsite[];
  theme: ThemeMode;
  onCloseSite: (id: string) => void;
}

export const WebsiteOverlay: React.FC<WebsiteOverlayProps> = ({
  sites,
  theme,
  onCloseSite,
}) => {
  const themeConfig = THEMES[theme];

  if (sites.length === 0) return null;

  return (
    <div className="fixed top-20 right-4 z-30 w-full max-w-sm flex flex-col gap-2">
      <AnimatePresence>
        {sites.map((site) => {
          const isSearch = site.title.startsWith('Search:');

          return (
            <motion.div
              key={site.id}
              initial={{ opacity: 0, x: 30, scale: 0.95 }}
              animate={{ opacity: 1, x: 0, scale: 1 }}
              exit={{ opacity: 0, x: 30, scale: 0.9 }}
              className="rounded-2xl glassmorphism border border-white/15 bg-slate-900/90 p-4 shadow-2xl backdrop-blur-xl"
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-center gap-2.5 min-w-0">
                  <div className={`p-2 rounded-xl bg-white/10 ${themeConfig.accentText}`}>
                    {isSearch ? <Search className="w-4 h-4" /> : <Globe className="w-4 h-4" />}
                  </div>
                  <div className="min-w-0">
                    <span className="text-[10px] font-mono text-cyan-400 uppercase tracking-wider block">
                      Browser Action Executed
                    </span>
                    <h4 className="text-sm font-semibold text-white tracking-tight truncate">
                      {site.title}
                    </h4>
                  </div>
                </div>

                <button
                  onClick={() => onCloseSite(site.id)}
                  className="p-1 rounded-lg text-slate-400 hover:text-white transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              <div className="mt-3 flex items-center justify-between gap-2 pt-2 border-t border-white/10">
                <span className="text-xs font-mono text-slate-400 truncate max-w-[200px]">
                  {site.url}
                </span>

                <a
                  href={site.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={`px-3 py-1.5 rounded-lg bg-white/10 text-xs font-medium text-white hover:bg-white/20 transition-all flex items-center gap-1.5 border border-white/10 ${themeConfig.accentText}`}
                >
                  <span>Open Link</span>
                  <ExternalLink className="w-3.5 h-3.5" />
                </a>
              </div>
            </motion.div>
          );
        })}
      </AnimatePresence>
    </div>
  );
};
