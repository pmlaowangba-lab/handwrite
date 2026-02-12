export interface HandwritingState {
  text: string;
  fontFamily: string;
  paperType: string;
  paperBackground: string;
  positionJitter: number;
  fontSize: number;
  lineHeight: number;
  scratchRate: number;
  weightVariation: number;
  noteSloppiness: number;
}

export interface FontOption {
  id: string;
  name: string;
  previewFont: string;
  category: string;
  sample: string;
}

export interface PaperSizeOption {
  id: string;
  label: string;
  width: number;
  height: number;
}

export interface PaperBackgroundOption {
  id: string;
  label: string;
  group: '纯色背景' | '真实纸张';
}
