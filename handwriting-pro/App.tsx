import React, { useState, useCallback } from 'react';
import { Header } from './components/Header';
import { Sidebar } from './components/Sidebar';
import { Preview } from './components/Preview';
import { DEFAULT_STATE } from './constants';
import { HandwritingState } from './types';

const App: React.FC = () => {
  const [state, setState] = useState<HandwritingState>(DEFAULT_STATE);
  const [seed, setSeed] = useState<number>(42);

  const handleStateChange = useCallback((newState: Partial<HandwritingState>) => {
    setState((prev) => ({ ...prev, ...newState }));
  }, []);

  const handleRegenerate = useCallback(() => {
    setSeed(Math.random() * 1000);
  }, []);

  return (
    <div className="text-navy-800 h-screen flex flex-col overflow-hidden selection:bg-accent selection:text-white font-sans bg-[#E8E6DF]">
      <Header />
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
