import React from 'react';

interface HeaderProps {
  onPrint: () => void;
  onExport: () => void;
  busyAction: 'print' | 'export' | null;
}

export const Header: React.FC<HeaderProps> = ({ onPrint, onExport, busyAction }) => {
  const isBusy = busyAction !== null;

  return (
    <header className="h-16 flex items-center justify-between px-8 bg-transparent z-50 shrink-0">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 bg-navy-800 rounded-xl flex items-center justify-center text-white shadow-xl">
          <span className="material-symbols-outlined text-xl">ink_pen</span>
        </div>
        <div>
          <h1 className="text-xl font-bold tracking-tight text-navy-800">
            老王手写体 <span className="font-normal text-navy-800/60 ml-1">Pro</span>
          </h1>
        </div>
      </div>
      <div className="flex items-center gap-2">
        <button
          className="flex items-center justify-center gap-2 py-2 px-4 rounded-xl bg-white text-navy-800 border border-gray-200 shadow-sm hover:shadow hover:bg-gray-50 text-sm font-semibold transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          onClick={onPrint}
          disabled={isBusy}
        >
          <span className="material-symbols-outlined text-lg">print</span>
          {busyAction === 'print' ? '打印中...' : '打印'}
        </button>
        <button
          className="flex items-center justify-center gap-2 py-2 px-4 rounded-xl bg-navy-800 text-white shadow-lg shadow-navy-800/20 hover:bg-navy-900 hover:shadow-xl text-sm font-semibold transition-all disabled:opacity-60 disabled:cursor-not-allowed"
          onClick={onExport}
          disabled={isBusy}
        >
          <span className="material-symbols-outlined text-lg">download</span>
          {busyAction === 'export' ? '导出中...' : '导出'}
        </button>
      </div>
    </header>
  );
};
