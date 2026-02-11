import React, { useMemo } from 'react';
import { HandwritingState } from '../types';
import { FONTS } from '../constants';

interface PreviewProps {
  state: HandwritingState;
  seed: number;
}

// Helper to generate consistent pseudo-random numbers
const seededRandom = (seed: number) => {
  const x = Math.sin(seed) * 10000;
  return x - Math.floor(x);
};

export const Preview: React.FC<PreviewProps> = ({ state, seed }) => {
  const activeFont = FONTS.find((f) => f.id === state.typeface)?.fontFamily || 'font-sans';
  
  // Calculate styles based on paper choice
  const paperStyles = useMemo(() => {
    const base = "w-[600px] shadow-paper rounded-[2px] p-16 relative transition-transform duration-500 transform";
    const size = state.paperSize === 'A4 Landscape' ? 'min-h-[600px] w-[850px]' : 'min-h-[850px] w-[600px]';
    
    // Background patterns
    let bgStyle: React.CSSProperties = {
      backgroundColor: '#fdfbf7',
      backgroundImage: `url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100' height='100' filter='url(%23noise)' opacity='0.08'/%3E%3C/svg%3E")`,
    };

    if (state.background === 'Grid White') {
       bgStyle.backgroundColor = '#ffffff';
       bgStyle.backgroundImage = `linear-gradient(#e5e7eb 1px, transparent 1px), linear-gradient(90deg, #e5e7eb 1px, transparent 1px)`;
       bgStyle.backgroundSize = '20px 20px';
    } else if (state.background === 'Lined Cream') {
       // We'll add lines via a pseudo element or keep the noise and add css gradient lines
       // For simplicity, let's just stick to the noise + custom lines in the render
    } else if (state.background === 'Plain Parchment') {
        bgStyle.backgroundColor = '#F3EFE0';
    }

    return { className: `${base} ${size}`, style: bgStyle };
  }, [state.paperSize, state.background]);


  // Split text and generate line-specific transforms
  const lines = useMemo(() => {
    return state.text.split('\n').map((line, index) => {
      // Generate random factors based on index + seed + chaos level
      const r = seededRandom(index * 13 + seed);
      const chaosFactor = state.chaos / 100;
      
      const rotation = (r - 0.5) * 4 * chaosFactor; // -2 to 2 degrees max
      const translateX = (seededRandom(index * 7 + seed) - 0.5) * 30 * chaosFactor;
      
      return {
        content: line,
        style: {
          transform: `rotate(${rotation}deg) translateX(${translateX}px)`,
          marginBottom: `${state.spacing}rem`,
        },
      };
    });
  }, [state.text, state.chaos, state.spacing, seed]);

  return (
    <section className="flex-1 relative flex flex-col items-center justify-center h-full">
      <div className="relative w-full h-full overflow-auto flex justify-center items-start p-8 custom-scrollbar">
        <div className={`bg-white ${paperStyles.className}`} style={paperStyles.style}>
            {/* Paper Overlay Effect */}
            <div className="absolute inset-0 pointer-events-none bg-gradient-to-br from-white/20 to-black/5" />
            
            {/* Red Margin Line */}
            {state.background === 'Lined Cream' && (
              <div className="absolute left-16 top-0 bottom-0 w-px bg-red-300/40" />
            )}

            {/* Paper Holes */}
            <div className="absolute left-0 top-0 bottom-0 w-16 flex flex-col items-center py-12 gap-8 opacity-60">
                <div className="w-3 h-3 rounded-full bg-gray-300/80 shadow-inner" />
                <div className="w-3 h-3 rounded-full bg-gray-300/80 shadow-inner" />
                <div className="w-3 h-3 rounded-full bg-gray-300/80 shadow-inner" />
            </div>

            {/* Content Container */}
            <div className={`ml-8 ${activeFont} text-2xl leading-[2.5rem] text-navy-800/90 tracking-wide relative z-10`}>
                
                {/* Lined Background Pattern for Text Area */}
                {state.background === 'Lined Cream' && (
                     <div 
                        className="absolute inset-0 -z-10 pointer-events-none" 
                        style={{
                            backgroundImage: 'linear-gradient(transparent 96%, rgba(0,0,0,0.06) 97%)',
                            backgroundSize: `100% ${2.5 * state.spacing}rem`, // Approximate scaling with spacing is hard without fixed line height, but visually okay
                            top: '0.4rem',
                            height: '100%',
                            backgroundAttachment: 'local'
                        }} 
                    />
                )}

                {lines.map((line, i) => (
                    <div 
                        key={i} 
                        className="relative inline-block w-full whitespace-pre-wrap break-words"
                        style={{
                           ...line.style,
                           marginBottom: `${state.spacing * 0.5}rem`, // visual spacing
                           textShadow: state.inkBlot > 0 ? `0 0 ${state.inkBlot * 0.5}px rgba(27, 42, 65, ${state.inkBlot * 0.05})` : 'none'
                        }}
                    >
                        {line.content || '\u00A0'}
                    </div>
                ))}
            </div>

            {/* Footer Metadata */}
            <div className="absolute bottom-12 right-12 text-xs font-mono text-gray-400/80 flex flex-col items-end gap-1">
                <p className="tracking-widest">NO. 001482</p>
                <p className="border-b border-gray-300/50 pb-0.5 w-24 text-right">
                    {new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                </p>
            </div>
        </div>
      </div>
    </section>
  );
};
