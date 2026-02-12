import React, { useEffect, useMemo, useRef, useState } from 'react';
import { HandwritingState } from '../types';
import { FONTS, PAPER_BACKGROUND_OPTIONS, PAPER_SIZE_OPTIONS } from '../constants';
import { renderPreviewCanvas } from '../utils/renderer';

interface PreviewProps {
  state: HandwritingState;
  seed: number;
}

export const Preview: React.FC<PreviewProps> = ({ state, seed }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [renderError, setRenderError] = useState<string | null>(null);
  const [isRendering, setIsRendering] = useState(false);

  const paperLabel = useMemo(
    () => PAPER_SIZE_OPTIONS.find((item) => item.id === state.paperType)?.label ?? state.paperType,
    [state.paperType],
  );
  const fontLabel = useMemo(
    () => FONTS.find((item) => item.id === state.fontFamily)?.name ?? state.fontFamily,
    [state.fontFamily],
  );
  const backgroundLabel = useMemo(
    () => PAPER_BACKGROUND_OPTIONS.find((item) => item.id === state.paperBackground)?.label ?? state.paperBackground,
    [state.paperBackground],
  );

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) {
      return;
    }

    let isActive = true;
    setIsRendering(true);
    setRenderError(null);

    renderPreviewCanvas(canvas, state, seed)
      .catch((error) => {
        if (isActive) {
          setRenderError(error instanceof Error ? error.message : '预览渲染失败');
        }
      })
      .finally(() => {
        if (isActive) {
          setIsRendering(false);
        }
      });

    return () => {
      isActive = false;
    };
  }, [state, seed]);

  return (
    <section className="flex-1 relative flex flex-col overflow-hidden">
      <div className="rounded-3xl border border-white/40 bg-white/65 backdrop-blur-xl shadow-card h-full flex flex-col">
        <div className="flex items-start justify-between border-b border-white/60 px-6 py-4 bg-gradient-to-r from-slate-50/90 to-blue-50/80 rounded-t-3xl">
          <div>
            <p className="text-[11px] uppercase tracking-[0.16em] text-navy-800/60">Live Preview</p>
            <h2 className="text-lg font-bold text-navy-800">手写画布</h2>
          </div>
          <div className="flex flex-wrap justify-end gap-2 max-w-[60%]">
            <span className="text-xs rounded-full px-2.5 py-1 bg-blue-100/70 text-blue-900 border border-blue-200/80">
              {paperLabel.split('(')[0].trim()}
            </span>
            <span className="text-xs rounded-full px-2.5 py-1 bg-indigo-100/70 text-indigo-900 border border-indigo-200/80">
              {fontLabel}
            </span>
            <span className="text-xs rounded-full px-2.5 py-1 bg-purple-100/70 text-purple-900 border border-purple-200/80">
              {backgroundLabel}
            </span>
            <span className="text-xs rounded-full px-2.5 py-1 bg-emerald-100/70 text-emerald-900 border border-emerald-200/80">
              {state.fontSize}px
            </span>
          </div>
        </div>

        <div className="relative w-full h-full overflow-auto custom-scrollbar p-6 flex justify-center">
          <div className="relative inline-flex">
            <canvas ref={canvasRef} className="max-w-none shadow-paper rounded-md bg-white" />
            {isRendering && (
              <div className="absolute inset-0 flex items-center justify-center bg-white/45 backdrop-blur-[1px] rounded-md">
                <span className="text-xs text-navy-800 bg-white/80 px-3 py-1 rounded-full border border-gray-200">
                  渲染中...
                </span>
              </div>
            )}
          </div>
        </div>

        {renderError && (
          <div className="mx-6 mb-6 mt-2 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            预览异常：{renderError}
          </div>
        )}
      </div>
    </section>
  );
};
