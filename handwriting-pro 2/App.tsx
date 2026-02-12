import React, { useState, useCallback } from 'react';
import { Header } from './components/Header';
import { Sidebar } from './components/Sidebar';
import { Preview } from './components/Preview';
import { DEFAULT_STATE } from './constants';
import { HandwritingState } from './types';
import { downloadExportImage, printExportImage } from './utils/renderer';

const App: React.FC = () => {
  const [state, setState] = useState<HandwritingState>(DEFAULT_STATE);
  const [seed, setSeed] = useState<number>(42);
  const [busyAction, setBusyAction] = useState<'print' | 'export' | null>(null);

  const handleStateChange = useCallback((newState: Partial<HandwritingState>) => {
    setState((prev) => ({ ...prev, ...newState }));
  }, []);

  const handleRegenerate = useCallback(() => {
    setSeed(Math.random() * 1000);
  }, []);

  const handleExport = useCallback(async () => {
    try {
      setBusyAction('export');
      await downloadExportImage(state, seed);
    } catch (error) {
      const message = error instanceof Error ? error.message : '导出失败';
      window.alert(message);
    } finally {
      setBusyAction(null);
    }
  }, [state, seed]);

  const handlePrint = useCallback(async () => {
    try {
      setBusyAction('print');
      await printExportImage(state, seed);
    } catch (error) {
      const message = error instanceof Error ? error.message : '打印失败';
      window.alert(message);
    } finally {
      setBusyAction(null);
    }
  }, [state, seed]);

  return (
    <div className="text-navy-800 h-screen flex flex-col overflow-hidden selection:bg-accent selection:text-white font-sans bg-[#E8E6DF]">
      <Header onPrint={handlePrint} onExport={handleExport} busyAction={busyAction} />
      <main className="flex-1 flex overflow-hidden p-6 pt-2 gap-8">
        <Sidebar
          state={state}
          onChange={handleStateChange}
          onRegenerate={handleRegenerate}
        />
        <Preview state={state} seed={seed} />
      </main>
    </div>
  );
};

export default App;
