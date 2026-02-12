import React from 'react';
import { HandwritingState } from '../types';
import { FONTS, PAPER_BACKGROUND_OPTIONS, PAPER_SIZE_OPTIONS } from '../constants';

interface SidebarProps {
  state: HandwritingState;
  onChange: (newState: Partial<HandwritingState>) => void;
  onRegenerate: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ state, onChange, onRegenerate }) => {
  const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    onChange({ text: e.target.value });
  };

  const realPaperOptions = PAPER_BACKGROUND_OPTIONS.filter((item) => item.group === '真实纸张');
  const solidPaperOptions = PAPER_BACKGROUND_OPTIONS.filter((item) => item.group === '纯色背景');

  return (
    <aside className="w-[420px] flex flex-col overflow-hidden shrink-0 h-full">
      <div className="flex-1 flex flex-col glass-panel rounded-3xl shadow-card border border-white/40 overflow-hidden bg-white/85 backdrop-blur-xl">
        <div className="p-6 flex-1 overflow-y-auto custom-scrollbar space-y-8">
          <section className="space-y-3">
            <div className="flex items-center justify-between">
              <label className="text-xs font-bold uppercase tracking-widest text-navy-800/60 flex items-center gap-2">
                <span className="material-symbols-outlined text-sm">edit_note</span> 文本内容
              </label>
              <span className="text-[10px] font-mono text-navy-800/50 bg-white/50 px-2 py-0.5 rounded-full">
                {state.text.length} / 8000
              </span>
            </div>
            <div className="relative">
              <textarea
                value={state.text}
                onChange={handleTextChange}
                className="w-full h-40 p-4 rounded-2xl border border-gray-200 bg-white/50 focus:bg-white focus:ring-2 focus:ring-navy-800/20 focus:border-navy-800 transition-all resize-none text-sm leading-relaxed shadow-inner-tight placeholder:text-gray-400 outline-none"
                placeholder="在这里输入你想转换的中文文案..."
              />
            </div>
          </section>

          <section className="space-y-3">
            <label className="text-xs font-bold uppercase tracking-widest text-navy-800/60 flex items-center gap-2">
              <span className="material-symbols-outlined text-sm">font_download</span> 字体选择
            </label>
            <div className="grid grid-cols-2 gap-3">
              {FONTS.map((font) => (
                <div
                  key={font.id}
                  onClick={() => onChange({ fontFamily: font.id })}
                  className={`cursor-pointer border-2 p-3 rounded-xl transition-all ${
                    state.fontFamily === font.id
                      ? 'border-navy-800 bg-white shadow-sm'
                      : 'border-transparent bg-white/50 hover:bg-white hover:border-navy-800/20'
                  }`}
                >
                  <div className={`text-lg mb-1 truncate ${font.previewFont}`}>
                    {font.sample}
                  </div>
                  <div className="text-[10px] text-gray-400 font-sans uppercase tracking-wide">
                    {font.name}
                  </div>
                </div>
              ))}
            </div>
          </section>

          <section className="space-y-6 pt-2">
            <label className="text-xs font-bold uppercase tracking-widest text-navy-800/60 flex items-center gap-2">
              <span className="material-symbols-outlined text-sm">tune</span> 视觉参数
            </label>

            <div className="space-y-3">
              <div className="flex justify-between items-end">
                <span className="text-xs font-medium text-navy-800">文字位置凌乱度</span>
                <span className="text-[10px] font-mono text-navy-800/60 bg-gray-100 px-1.5 py-0.5 rounded">
                  {state.positionJitter}%
                </span>
              </div>
              <div className="relative h-6 flex items-center">
                <input
                  type="range"
                  className="w-full"
                  min="0"
                  max="100"
                  value={state.positionJitter}
                  onChange={(e) => onChange({ positionJitter: parseInt(e.target.value, 10) })}
                />
              </div>
            </div>

            <div className="space-y-3">
              <div className="flex justify-between items-end">
                <span className="text-xs font-medium text-navy-800">字号大小</span>
                <span className="text-[10px] font-mono text-navy-800/60 bg-gray-100 px-1.5 py-0.5 rounded">
                  {state.fontSize}px
                </span>
              </div>
              <div className="relative h-6 flex items-center">
                <input
                  type="range"
                  className="w-full"
                  min="16"
                  max="48"
                  value={state.fontSize}
                  onChange={(e) => onChange({ fontSize: parseInt(e.target.value, 10) })}
                />
              </div>
            </div>

            <div className="space-y-3">
              <div className="flex justify-between items-end">
                <span className="text-xs font-medium text-navy-800">行间距</span>
                <span className="text-[10px] font-mono text-navy-800/60 bg-gray-100 px-1.5 py-0.5 rounded">
                  {state.lineHeight.toFixed(1)}
                </span>
              </div>
              <div className="relative h-6 flex items-center">
                <input
                  type="range"
                  className="w-full"
                  min="1.2"
                  max="3.0"
                  step="0.1"
                  value={state.lineHeight}
                  onChange={(e) => onChange({ lineHeight: parseFloat(e.target.value) })}
                />
              </div>
            </div>

            <div className="space-y-3">
              <div className="flex justify-between items-end">
                <span className="text-xs font-medium text-navy-800">随机涂改概率</span>
                <span className="text-[10px] font-mono text-navy-800/60 bg-gray-100 px-1.5 py-0.5 rounded">
                  {state.scratchRate}%
                </span>
              </div>
              <div className="relative h-6 flex items-center">
                <input
                  type="range"
                  className="w-full"
                  min="0"
                  max="100"
                  value={state.scratchRate}
                  onChange={(e) => onChange({ scratchRate: parseInt(e.target.value, 10) })}
                />
              </div>
            </div>

            <div className="space-y-3">
              <div className="flex justify-between items-end">
                <span className="text-xs font-medium text-navy-800">字体笔画凌乱度</span>
                <span className="text-[10px] font-mono text-navy-800/60 bg-gray-100 px-1.5 py-0.5 rounded">
                  {state.weightVariation}%
                </span>
              </div>
              <div className="relative h-6 flex items-center">
                <input
                  type="range"
                  className="w-full"
                  min="0"
                  max="100"
                  value={state.weightVariation}
                  onChange={(e) => onChange({ weightVariation: parseInt(e.target.value, 10) })}
                />
              </div>
            </div>

            <div className="space-y-3">
              <div className="flex justify-between items-end">
                <span className="text-xs font-medium text-navy-800">笔记潦草</span>
                <span className="text-[10px] font-mono text-navy-800/60 bg-gray-100 px-1.5 py-0.5 rounded">
                  {state.noteSloppiness}%
                </span>
              </div>
              <div className="relative h-6 flex items-center">
                <input
                  type="range"
                  className="w-full"
                  min="0"
                  max="100"
                  value={state.noteSloppiness}
                  onChange={(e) => onChange({ noteSloppiness: parseInt(e.target.value, 10) })}
                />
              </div>
            </div>

            <div className="flex flex-col gap-4 pt-2">
              <div className="space-y-1.5">
                <label className="text-[10px] font-semibold text-gray-500 uppercase">纸张尺寸</label>
                <select
                  className="w-full bg-white/50 border-gray-200 rounded-lg text-sm focus:ring-navy-800 focus:border-navy-800 py-2 outline-none"
                  value={state.paperType}
                  onChange={(e) => onChange({ paperType: e.target.value })}
                >
                  {PAPER_SIZE_OPTIONS.map((option) => (
                    <option key={option.id} value={option.id}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>
              <div className="space-y-1.5">
                <label className="text-[10px] font-semibold text-gray-500 uppercase">纸张背景</label>
                <select
                  className="w-full bg-white/50 border-gray-200 rounded-lg text-sm focus:ring-navy-800 focus:border-navy-800 py-2 outline-none"
                  value={state.paperBackground}
                  onChange={(e) => onChange({ paperBackground: e.target.value })}
                >
                  <optgroup label="纯色背景">
                    {solidPaperOptions.map((option) => (
                      <option key={option.id} value={option.id}>
                        {option.label}
                      </option>
                    ))}
                  </optgroup>
                  <optgroup label="真实纸张">
                    {realPaperOptions.map((option) => (
                      <option key={option.id} value={option.id}>
                        {option.label}
                      </option>
                    ))}
                  </optgroup>
                </select>
              </div>
            </div>
          </section>
        </div>

        <div className="p-6 bg-white/40 border-t border-white/50 backdrop-blur-md">
          <button
            onClick={onRegenerate}
            className="w-full flex items-center justify-center gap-2 py-3 px-4 rounded-xl bg-navy-800 text-white shadow-lg shadow-navy-800/20 hover:bg-navy-900 hover:shadow-xl text-sm font-semibold transition-all"
          >
            <span className="material-symbols-outlined text-lg">history_edu</span>
            刷新预览（重置随机感）
          </button>
        </div>
      </div>
    </aside>
  );
};
