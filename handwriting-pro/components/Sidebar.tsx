import React from 'react';
import { HandwritingState, FontOption } from '../types';
import { FONTS } from '../constants';

interface SidebarProps {
  state: HandwritingState;
  onChange: (newState: Partial<HandwritingState>) => void;
  onRegenerate: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ state, onChange, onRegenerate }) => {
  const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    onChange({ text: e.target.value });
  };

  const handleFontSelect = (fontId: string) => {
    onChange({ typeface: fontId as HandwritingState['typeface'] });
  };

  return (
    <aside className="w-[420px] flex flex-col overflow-hidden shrink-0 h-full">
      <div className="flex-1 flex flex-col glass-panel rounded-3xl shadow-card border border-white/40 overflow-hidden bg-white/85 backdrop-blur-xl">
        <div className="p-6 flex-1 overflow-y-auto custom-scrollbar space-y-8">
          
          {/* Content Section */}
          <section className="space-y-3">
            <div className="flex items-center justify-between">
              <label className="text-xs font-bold uppercase tracking-widest text-navy-800/60 flex items-center gap-2">
                <span className="material-symbols-outlined text-sm">edit_note</span> Content
              </label>
              <span className="text-[10px] font-mono text-navy-800/50 bg-white/50 px-2 py-0.5 rounded-full">
                {state.text.length} / 5000
              </span>
            </div>
            <div className="relative group">
              <textarea
                value={state.text}
                onChange={handleTextChange}
                className="w-full h-40 p-4 rounded-2xl border border-gray-200 bg-white/50 focus:bg-white focus:ring-2 focus:ring-navy-800/20 focus:border-navy-800 transition-all resize-none text-sm leading-relaxed shadow-inner-tight placeholder:text-gray-400 outline-none"
                placeholder="Start typing your masterpiece..."
              />
              <button 
                className="absolute bottom-3 right-3 p-1.5 bg-white shadow-sm rounded-lg hover:text-accent transition-colors border border-gray-100 opacity-0 group-hover:opacity-100 translate-y-2 group-hover:translate-y-0 duration-200" 
                title="AI Enhance"
              >
                <span className="material-symbols-outlined text-lg">auto_awesome</span>
              </button>
            </div>
          </section>

          {/* Typeface Section */}
          <section className="space-y-3">
            <label className="text-xs font-bold uppercase tracking-widest text-navy-800/60 flex items-center gap-2">
              <span className="material-symbols-outlined text-sm">font_download</span> Typeface
            </label>
            <div className="grid grid-cols-2 gap-3">
              {FONTS.map((font) => (
                <div
                  key={font.id}
                  onClick={() => handleFontSelect(font.id)}
                  className={`cursor-pointer border-2 p-3 rounded-xl transition-all ${
                    state.typeface === font.id
                      ? 'border-navy-800 bg-white shadow-sm'
                      : 'border-transparent bg-white/50 hover:bg-white hover:border-navy-800/20'
                  }`}
                >
                  <div className={`text-lg mb-1 truncate ${font.fontFamily}`}>
                    {font.name}
                  </div>
                  <div className="text-[10px] text-gray-400 font-sans uppercase tracking-wide">
                    {font.category}
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* Adjustments Section */}
          <section className="space-y-6 pt-2">
            <label className="text-xs font-bold uppercase tracking-widest text-navy-800/60 flex items-center gap-2">
              <span className="material-symbols-outlined text-sm">tune</span> Adjustments
            </label>

            {/* Spacing */}
            <div className="space-y-3">
              <div className="flex justify-between items-end">
                <span className="text-xs font-medium text-navy-800">Spacing</span>
                <span className="text-[10px] font-mono text-navy-800/60 bg-gray-100 px-1.5 py-0.5 rounded">
                  {state.spacing}
                </span>
              </div>
              <div className="relative h-6 flex items-center">
                <input
                  type="range"
                  min="1"
                  max="3"
                  step="0.1"
                  value={state.spacing}
                  onChange={(e) => onChange({ spacing: parseFloat(e.target.value) })}
                />
              </div>
            </div>

            {/* Chaos */}
            <div className="space-y-3">
              <div className="flex justify-between items-end">
                <span className="text-xs font-medium text-navy-800">Chaos</span>
                <span className="text-[10px] font-mono text-navy-800/60 bg-gray-100 px-1.5 py-0.5 rounded">
                  {state.chaos}%
                </span>
              </div>
              <div className="relative h-6 flex items-center">
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={state.chaos}
                  onChange={(e) => onChange({ chaos: parseInt(e.target.value) })}
                />
              </div>
            </div>

            {/* Ink Blot */}
            <div className="space-y-3">
              <div className="flex justify-between items-end">
                <span className="text-xs font-medium text-navy-800">Ink Blot</span>
                <span className="text-[10px] font-mono text-navy-800/60 bg-gray-100 px-1.5 py-0.5 rounded">
                  {state.inkBlot}%
                </span>
              </div>
              <div className="relative h-6 flex items-center">
                <input
                  type="range"
                  min="0"
                  max="20"
                  value={state.inkBlot}
                  onChange={(e) => onChange({ inkBlot: parseInt(e.target.value) })}
                />
              </div>
            </div>

            {/* Dropdowns */}
            <div className="flex flex-col gap-4 pt-2">
              <div className="space-y-1.5">
                <label className="text-[10px] font-semibold text-gray-500 uppercase">Paper Size</label>
                <select 
                  className="w-full bg-white/50 border-gray-200 rounded-lg text-sm focus:ring-navy-800 focus:border-navy-800 py-2 outline-none"
                  value={state.paperSize}
                  onChange={(e) => onChange({ paperSize: e.target.value as any })}
                >
                  <option>A4 Portrait</option>
                  <option>A4 Landscape</option>
                </select>
              </div>
              <div className="space-y-1.5">
                <label className="text-[10px] font-semibold text-gray-500 uppercase">Background</label>
                <select 
                  className="w-full bg-white/50 border-gray-200 rounded-lg text-sm focus:ring-navy-800 focus:border-navy-800 py-2 outline-none"
                  value={state.background}
                  onChange={(e) => onChange({ background: e.target.value as any })}
                >
                  <option>Lined Cream</option>
                  <option>Grid White</option>
                  <option>Plain Parchment</option>
                </select>
              </div>
            </div>
          </section>
        </div>

        {/* Footer Actions */}
        <div className="p-6 bg-white/40 border-t border-white/50 backdrop-blur-md">
          <button 
            onClick={onRegenerate}
            className="w-full flex items-center justify-center gap-2 py-3 px-4 rounded-xl bg-navy-800 text-white shadow-lg shadow-navy-800/20 hover:bg-navy-900 hover:shadow-xl text-sm font-semibold transition-all"
          >
            <span className="material-symbols-outlined text-lg">history_edu</span>
            Generate Preview
          </button>
        </div>
      </div>
    </aside>
  );
};
