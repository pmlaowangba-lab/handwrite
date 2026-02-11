export interface HandwritingState {
  text: string;
  typeface: 'Ma Shan Zheng' | 'Caveat' | 'Kalam';
  spacing: number;
  chaos: number;
  inkBlot: number;
  paperSize: 'A4 Portrait' | 'A4 Landscape';
  background: 'Lined Cream' | 'Grid White' | 'Plain Parchment';
}

export interface FontOption {
  id: string;
  name: string;
  fontFamily: string;
  category: string;
}
