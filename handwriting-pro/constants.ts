import { FontOption, HandwritingState } from './types';

export const DEFAULT_STATE: HandwritingState = {
  text: `这是一段手写体测试文字。
你可以输入任何内容，
系统会自动生成手写效果。
适合用于视频录制、
笔记展示等场景。`,
  typeface: 'Ma Shan Zheng',
  spacing: 1.8,
  chaos: 61,
  inkBlot: 3,
  paperSize: 'A4 Portrait',
  background: 'Lined Cream',
};

export const FONTS: FontOption[] = [
  {
    id: 'Ma Shan Zheng',
    name: '清新手写体',
    fontFamily: 'font-handwriting',
    category: 'Selected',
  },
  {
    id: 'Caveat',
    name: 'Caveat Brush',
    fontFamily: 'font-caveat',
    category: 'Latin',
  },
  {
    id: 'Kalam',
    name: 'Kalam Regular',
    fontFamily: 'font-kalam',
    category: 'Mixed',
  },
];
