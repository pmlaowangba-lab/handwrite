import { FontOption, HandwritingState } from './types';

export const DEFAULT_STATE: HandwritingState = {
  text: `这是一段手写体测试文字。
你可以输入任何内容，
系统会自动生成手写效果。
适合用于视频录制、
笔记展示等场景。`,
  fontFamily: '清松手写体5-行楷',
  paperType: 'a4-portrait',
  paperBackground: 'white',
  positionJitter: 10,
  fontSize: 24,
  lineHeight: 1.8,
  scratchRate: 3,
  weightVariation: 5,
  noteSloppiness: 12,
};

export const FONTS: FontOption[] = [
  {
    id: '清松手写体1-圆润',
    name: '清松手写体1-圆润',
    previewFont: 'font-qingsong-1',
    category: '清松系列',
    sample: '圆润自然',
  },
  {
    id: '清松手写体2-秀气',
    name: '清松手写体2-秀气',
    previewFont: 'font-qingsong-2',
    category: '清松系列',
    sample: '细腻秀气',
  },
  {
    id: '清松手写体3-呆萌',
    name: '清松手写体3-呆萌',
    previewFont: 'font-qingsong-3',
    category: '清松系列',
    sample: '可爱亲和',
  },
  {
    id: '清松手写体4-POP',
    name: '清松手写体4-POP',
    previewFont: 'font-qingsong-4',
    category: '清松系列',
    sample: '活泼跳跃',
  },
  {
    id: '清松手写体5-行楷',
    name: '清松手写体5-行楷',
    previewFont: 'font-qingsong-5',
    category: '清松系列',
    sample: '行楷流畅',
  },
  {
    id: '清松手写体6-Q萌',
    name: '清松手写体6-Q萌',
    previewFont: 'font-qingsong-6',
    category: '清松系列',
    sample: 'Q萌俏皮',
  },
  {
    id: '清松手写体7-飘逸',
    name: '清松手写体7-飘逸',
    previewFont: 'font-qingsong-7',
    category: '清松系列',
    sample: '飘逸洒脱',
  },
  {
    id: '清松手写体8-随性',
    name: '清松手写体8-随性',
    previewFont: 'font-qingsong-8',
    category: '清松系列',
    sample: '随性潇洒',
  },
  {
    id: '沐瑶软笔手写体',
    name: '沐瑶软笔手写体',
    previewFont: 'font-muyao-1',
    category: '沐瑶系列',
    sample: '软笔质感',
  },
  {
    id: '沐瑶随心手写体',
    name: '沐瑶随心手写体',
    previewFont: 'font-muyao-2',
    category: '沐瑶系列',
    sample: '轻松自然',
  },
  {
    id: '内海字体',
    name: '内海字体',
    previewFont: 'font-neihai',
    category: '特色字体',
    sample: '沉稳日常',
  },
  {
    id: '她屿山海',
    name: '她屿山海',
    previewFont: 'font-shanhai',
    category: '特色字体',
    sample: '山海文艺',
  },
  {
    id: '栗壳坚坚体',
    name: '栗壳坚坚体',
    previewFont: 'font-like',
    category: '特色字体',
    sample: '硬朗有力',
  },
];

export const PAPER_SIZE_OPTIONS = [
  { id: 'a4-portrait', label: 'A4纸-纵向 (4960x7015)', width: 4960, height: 7015 },
  { id: 'a4-landscape', label: 'A4纸-横向 (7015x4960)', width: 7015, height: 4960 },
  { id: 'b5-portrait', label: 'B5纸-纵向 (4157x5905)', width: 4157, height: 5905 },
  { id: 'b5-landscape', label: 'B5纸-横向 (5905x4157)', width: 5905, height: 4157 },
  { id: 'a3-portrait', label: 'A3纸-纵向 (7015x9921)', width: 7015, height: 9921 },
  { id: 'a3-landscape', label: 'A3纸-横向 (9921x7015)', width: 9921, height: 7015 },
];

export const PAPER_SIZES = PAPER_SIZE_OPTIONS.reduce<Record<string, { w: number; h: number }>>((acc, item) => {
  acc[item.id] = { w: item.width, h: item.height };
  return acc;
}, {});

export const PAPER_BACKGROUND_OPTIONS = [
  { id: 'white', label: '纯白色', group: '纯色背景' },
  { id: 'cream', label: '#FFF8DC 米黄色', group: '纯色背景' },
  { id: 'lightgray', label: '#F5F5F5 浅灰色', group: '纯色背景' },
  { id: 'real-grid-white', label: '方格纸-白色', group: '真实纸张' },
  { id: 'real-blank-white', label: '空白纸-白色', group: '真实纸张' },
  { id: 'real-lined-cream', label: '横线纸-米黄', group: '真实纸张' },
  { id: 'real-lined-vintage', label: '横线纸-复古', group: '真实纸张' },
  { id: 'real-blank-used', label: '使用痕迹纸', group: '真实纸张' },
] as const;

export const PAPER_BACKGROUNDS: Record<
  string,
  { type: 'color'; value: string } | { type: 'image'; src: string }
> = {
  white: { type: 'color', value: '#ffffff' },
  cream: { type: 'color', value: '#FFF8DC' },
  lightgray: { type: 'color', value: '#F5F5F5' },
  'real-grid-white': { type: 'image', src: '/papers/processed/grid-white-clean.jpg' },
  'real-blank-white': { type: 'image', src: '/papers/processed/blank-white.jpg' },
  'real-lined-cream': { type: 'image', src: '/papers/processed/lined-cream-new.jpg' },
  'real-lined-vintage': { type: 'image', src: '/papers/processed/lined-yellow-vintage.jpg' },
  'real-blank-used': { type: 'image', src: '/papers/processed/blank-used-marks.jpg' },
};
