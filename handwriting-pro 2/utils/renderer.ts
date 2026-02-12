import { DEFAULT_STATE, PAPER_BACKGROUNDS, PAPER_SIZES } from '../constants';
import { HandwritingState } from '../types';

const PREVIEW_BASE_WIDTH = 700;
const REAL_PAPER_BASE_LINEHEIGHT = 1.8;

type DrawRect = { x: number; y: number; w: number; h: number };

type PaperLayout = {
  left: number;
  right: number;
  top: number;
  bottom: number;
  rowAdvance: number;
  lineSnapped: boolean;
  naturalLineStep: number | null;
};

type RealPaperLayoutConfig = {
  leftRatio: number;
  rightRatio: number;
  topRatio: number;
  bottomRatio: number;
  topLineRatio?: number;
  lineStepRatio?: number;
};

const realPaperLayouts: Record<string, RealPaperLayoutConfig> = {
  'real-grid-white': {
    leftRatio: 0.08,
    rightRatio: 0.08,
    topLineRatio: 0.045,
    topRatio: 0.075,
    bottomRatio: 0.065,
    lineStepRatio: 48 / 1986,
  },
  'real-lined-cream': {
    leftRatio: 0.09,
    rightRatio: 0.14,
    topLineRatio: 0.068,
    topRatio: 0.09,
    bottomRatio: 0.09,
    lineStepRatio: 66 / 1796,
  },
  'real-lined-vintage': {
    leftRatio: 0.085,
    rightRatio: 0.085,
    topLineRatio: 0.073,
    topRatio: 0.1,
    bottomRatio: 0.1,
    lineStepRatio: 70 / 1932,
  },
  'real-blank-white': {
    leftRatio: 0.08,
    rightRatio: 0.08,
    topRatio: 0.09,
    bottomRatio: 0.085,
  },
  'real-blank-used': {
    leftRatio: 0.08,
    rightRatio: 0.08,
    topRatio: 0.09,
    bottomRatio: 0.09,
  },
};

const bgImageCache: Record<string, HTMLImageElement> = {};

const getSafeState = (state: HandwritingState): HandwritingState => ({
  ...DEFAULT_STATE,
  ...state,
});

const getPaperSize = (paperType: string) => PAPER_SIZES[paperType] ?? PAPER_SIZES[DEFAULT_STATE.paperType];

const ensureFontReady = async (fontFamily: string, fontSize: number) => {
  try {
    if (!('fonts' in document) || !document.fonts) {
      return;
    }
    await document.fonts.load(`${Math.max(16, fontSize)}px "${fontFamily}"`);
    await document.fonts.ready;
  } catch (error) {
    console.warn(`Font preload warning for ${fontFamily}:`, error);
  }
};

const seededRandom = (seed: number) => {
  let value = seed >>> 0;
  return () => {
    value += 0x6d2b79f5;
    let t = Math.imul(value ^ (value >>> 15), 1 | value);
    t ^= t + Math.imul(t ^ (t >>> 7), 61 | t);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
};

const getBackgroundDrawRect = (
  targetWidth: number,
  targetHeight: number,
  imageWidth: number,
  imageHeight: number,
): DrawRect => {
  if (!imageWidth || !imageHeight) {
    return { x: 0, y: 0, w: targetWidth, h: targetHeight };
  }

  const scale = Math.min(targetWidth / imageWidth, targetHeight / imageHeight);
  const drawWidth = imageWidth * scale;
  const drawHeight = imageHeight * scale;

  return {
    x: (targetWidth - drawWidth) / 2,
    y: (targetHeight - drawHeight) / 2,
    w: drawWidth,
    h: drawHeight,
  };
};

const drawPaperBackground = (
  drawCtx: CanvasRenderingContext2D,
  bgKey: string,
  targetWidth: number,
  targetHeight: number,
  bgImage: HTMLImageElement | null,
): DrawRect => {
  const bgConfig = PAPER_BACKGROUNDS[bgKey] ?? PAPER_BACKGROUNDS.white;
  let drawRect: DrawRect = { x: 0, y: 0, w: targetWidth, h: targetHeight };

  if (bgConfig.type === 'color') {
    drawCtx.fillStyle = bgConfig.value;
    drawCtx.fillRect(0, 0, targetWidth, targetHeight);
    return drawRect;
  }

  drawCtx.fillStyle = '#ffffff';
  drawCtx.fillRect(0, 0, targetWidth, targetHeight);

  if (bgImage) {
    drawRect = getBackgroundDrawRect(targetWidth, targetHeight, bgImage.width, bgImage.height);
    drawCtx.drawImage(bgImage, drawRect.x, drawRect.y, drawRect.w, drawRect.h);
  }

  return drawRect;
};

const getTextAscent = (drawCtx: CanvasRenderingContext2D, fontSize: number) => {
  const metrics = drawCtx.measureText('测Ag');
  if (metrics && Number.isFinite(metrics.actualBoundingBoxAscent) && metrics.actualBoundingBoxAscent > 0) {
    return metrics.actualBoundingBoxAscent;
  }
  return fontSize * 0.78;
};

const getPaperTextLayout = ({
  drawCtx,
  paperBg,
  targetWidth,
  targetHeight,
  drawRect,
  fontSize,
  lineHeight,
}: {
  drawCtx: CanvasRenderingContext2D;
  paperBg: string;
  targetWidth: number;
  targetHeight: number;
  drawRect: DrawRect;
  fontSize: number;
  lineHeight: number;
}): PaperLayout => {
  const basePadding = 60 * (targetWidth / PREVIEW_BASE_WIDTH);
  const config = realPaperLayouts[paperBg];
  const hasRealPaperConfig = Boolean(config);

  if (!hasRealPaperConfig) {
    return {
      left: basePadding,
      right: targetWidth - basePadding,
      top: basePadding,
      bottom: targetHeight - basePadding,
      rowAdvance: fontSize * lineHeight,
      lineSnapped: false,
      naturalLineStep: null,
    };
  }

  const leftPadding = Math.max(basePadding * 0.65, drawRect.w * config.leftRatio);
  const rightPadding = Math.max(basePadding * 0.65, drawRect.w * config.rightRatio);
  const bottomPadding = Math.max(basePadding * 0.5, drawRect.h * config.bottomRatio);

  const left = drawRect.x + leftPadding;
  const right = drawRect.x + drawRect.w - rightPadding;
  const bottom = drawRect.y + drawRect.h - bottomPadding;

  let top = drawRect.y + Math.max(basePadding * 0.45, drawRect.h * config.topRatio);
  let rowAdvance = fontSize * lineHeight;
  let lineSnapped = false;
  let naturalLineStep: number | null = null;

  if (config.lineStepRatio && config.topLineRatio !== undefined) {
    naturalLineStep = drawRect.h * config.lineStepRatio;
    const sliderFactor = lineHeight / REAL_PAPER_BASE_LINEHEIGHT;
    rowAdvance = naturalLineStep * sliderFactor;

    const baselineY = drawRect.y + drawRect.h * config.topLineRatio;
    top = baselineY - getTextAscent(drawCtx, fontSize);
    lineSnapped = true;
  }

  return {
    left,
    right,
    top: Math.max(drawRect.y, top),
    bottom,
    rowAdvance,
    lineSnapped,
    naturalLineStep,
  };
};

const preloadBackgroundImage = (bgKey: string) =>
  new Promise<HTMLImageElement | null>((resolve, reject) => {
    const bgConfig = PAPER_BACKGROUNDS[bgKey];
    if (!bgConfig || bgConfig.type !== 'image') {
      resolve(null);
      return;
    }

    if (bgImageCache[bgKey]) {
      resolve(bgImageCache[bgKey]);
      return;
    }

    const image = new Image();
    image.onload = () => {
      bgImageCache[bgKey] = image;
      resolve(image);
    };
    image.onerror = () => reject(new Error(`Failed to load ${bgConfig.src}`));
    image.src = bgConfig.src;
  });

const drawCharacter = ({
  drawCtx,
  char,
  finalX,
  finalY,
  charWidth,
  fontSize,
  weightVariation,
  sloppiness,
  random,
}: {
  drawCtx: CanvasRenderingContext2D;
  char: string;
  finalX: number;
  finalY: number;
  charWidth: number;
  fontSize: number;
  weightVariation: number;
  sloppiness: number;
  random: () => number;
}) => {
  const rotateAngle = (random() - 0.5) * 0.18 * sloppiness;

  const paintGlyph = (offsetX = 0, offsetY = 0, alpha = 1) => {
    drawCtx.save();
    drawCtx.globalAlpha *= alpha;

    if (Math.abs(rotateAngle) > 0.001) {
      drawCtx.translate(finalX + charWidth * 0.5 + offsetX, finalY + fontSize * 0.5 + offsetY);
      drawCtx.rotate(rotateAngle);
      drawCtx.fillText(char, -charWidth * 0.5, -fontSize * 0.5);
    } else {
      drawCtx.fillText(char, finalX + offsetX, finalY + offsetY);
    }

    drawCtx.restore();
  };

  const shouldVaryWeight = random() < weightVariation;
  if (shouldVaryWeight) {
    const extraWeight = 1 + Math.floor(random() * 3);
    for (let index = 0; index < extraWeight; index += 1) {
      const microOffsetX = index * 0.5;
      const microOffsetY = (random() - 0.5) * 0.2;
      paintGlyph(microOffsetX, microOffsetY, 0.86);
    }
  }

  paintGlyph();

  if (sloppiness > 0 && random() < sloppiness * 0.45) {
    const ghostOffsetX = (random() - 0.5) * 1.6;
    const ghostOffsetY = (random() - 0.5) * 1.8;
    paintGlyph(ghostOffsetX, ghostOffsetY, 0.32);
  }
};

const drawScratchLine = ({
  drawCtx,
  x,
  y,
  fontSize,
  charWidth,
  random,
  sloppiness,
}: {
  drawCtx: CanvasRenderingContext2D;
  x: number;
  y: number;
  fontSize: number;
  charWidth: number;
  random: () => number;
  sloppiness: number;
}) => {
  drawCtx.save();
  drawCtx.strokeStyle = '#1e1e1e';
  drawCtx.fillStyle = '#1e1e1e';

  const scratchType = random();
  const charW = Math.max(charWidth * 0.95, fontSize * 0.7);
  const charH = fontSize * 0.85;

  if (scratchType < 0.6) {
    drawCtx.lineWidth = 1.2 + sloppiness * 0.9;
    drawCtx.globalAlpha = 0.7;
    const lineCount = 4 + Math.floor(random() * (3 + Math.round(sloppiness * 2)));
    for (let index = 0; index < lineCount; index += 1) {
      const lineY = y + charH * 0.15 + ((charH * 0.7) / lineCount) * index;
      const jitterY = (random() - 0.5) * (2 + sloppiness * 3);
      drawCtx.beginPath();
      drawCtx.moveTo(x - 2, lineY + jitterY);
      const midX = x + charW * 0.5;
      const midJitter = (random() - 0.5) * (3 + sloppiness * 4);
      drawCtx.quadraticCurveTo(midX, lineY + midJitter, x + charW + 2, lineY + (random() - 0.5) * 2);
      drawCtx.stroke();
    }
  } else if (scratchType < 0.85) {
    drawCtx.globalAlpha = 0.55;
    drawCtx.fillRect(x - 1, y + charH * 0.05, charW + 2, charH * 0.9);
    drawCtx.globalAlpha = 0.3;
    drawCtx.lineWidth = 2 + sloppiness * 0.6;
    for (let index = 0; index < 3; index += 1) {
      const lineY = y + charH * 0.2 + ((charH * 0.6) / 3) * index;
      drawCtx.beginPath();
      drawCtx.moveTo(x - 2, lineY + (random() - 0.5) * (2 + sloppiness * 2));
      drawCtx.lineTo(x + charW + 2, lineY + (random() - 0.5) * (2 + sloppiness * 2));
      drawCtx.stroke();
    }
  } else {
    drawCtx.lineWidth = 1.5 + sloppiness * 0.5;
    drawCtx.globalAlpha = 0.6;
    const centerX = x + charW * 0.5;
    const centerY = y + charH * 0.5;
    const radiusX = charW * (0.55 + sloppiness * 0.15);
    const radiusY = charH * (0.5 + sloppiness * 0.15);
    drawCtx.beginPath();
    drawCtx.ellipse(centerX, centerY, radiusX, radiusY, (random() - 0.5) * (0.2 + sloppiness * 0.3), 0, Math.PI * 2);
    drawCtx.stroke();
  }

  drawCtx.restore();
};

const drawTextContent = ({
  drawCtx,
  state,
  width,
  height,
  drawRect,
  fontSize,
  random,
}: {
  drawCtx: CanvasRenderingContext2D;
  state: HandwritingState;
  width: number;
  height: number;
  drawRect: DrawRect;
  fontSize: number;
  random: () => number;
}) => {
  drawCtx.font = `${fontSize}px "${state.fontFamily}", cursive`;
  drawCtx.fillStyle = '#1e1e1e';
  drawCtx.textBaseline = 'top';

  const layout = getPaperTextLayout({
    drawCtx,
    paperBg: state.paperBackground,
    targetWidth: width,
    targetHeight: height,
    drawRect,
    fontSize,
    lineHeight: state.lineHeight,
  });

  const lines = (state.text ?? '').split('\n');
  const positionJitter = state.positionJitter / 100;
  const scratchRate = state.scratchRate / 100;
  const weightVariation = state.weightVariation / 100;
  const sloppiness = state.noteSloppiness / 100;

  let y = layout.top;
  let reachedBottom = false;

  for (const line of lines) {
    let x = layout.left;

    for (const char of line) {
      const metrics = drawCtx.measureText(char);
      const charWidth = metrics.width + 2;

      if (x + charWidth > layout.right && x > layout.left) {
        x = layout.left;
        y += layout.rowAdvance;
      }

      if (y + fontSize > layout.bottom) {
        reachedBottom = true;
        break;
      }

      const maxOffsetX = fontSize * positionJitter * (0.8 + sloppiness * 0.35);
      const maxOffsetY = layout.lineSnapped
        ? Math.min(layout.rowAdvance * (0.18 + sloppiness * 0.18), fontSize * positionJitter * (0.22 + sloppiness * 0.18))
        : fontSize * positionJitter * (0.4 + sloppiness * 0.3);
      const offsetX = (random() - 0.5) * maxOffsetX + (random() - 0.5) * fontSize * sloppiness * 0.2;
      const offsetY = (random() - 0.5) * maxOffsetY + (random() - 0.5) * fontSize * sloppiness * 0.18;

      const maxX = Math.max(layout.left, layout.right - charWidth);
      const finalX = Math.min(maxX, Math.max(layout.left, x + offsetX));
      const finalY = y + offsetY;

      drawCharacter({
        drawCtx,
        char,
        finalX,
        finalY,
        charWidth,
        fontSize,
        weightVariation,
        sloppiness,
        random,
      });

      if (random() < scratchRate) {
        drawScratchLine({
          drawCtx,
          x: finalX,
          y: finalY,
          fontSize,
          charWidth,
          random,
          sloppiness,
        });
      }

      x += charWidth;
    }

    if (reachedBottom) {
      break;
    }

    y += layout.rowAdvance;
    if (y > layout.bottom) {
      break;
    }
  }
};

const renderInternal = async ({
  canvas,
  state,
  seed,
  mode,
}: {
  canvas: HTMLCanvasElement;
  state: HandwritingState;
  seed: number;
  mode: 'preview' | 'export';
}) => {
  const safeState = getSafeState(state);
  const paper = getPaperSize(safeState.paperType);
  const previewScale = PREVIEW_BASE_WIDTH / paper.w;
  const fontScale = mode === 'preview' ? 1 : paper.w / PREVIEW_BASE_WIDTH;
  const targetFontSize = safeState.fontSize * fontScale;

  const width = mode === 'preview' ? Math.round(paper.w * previewScale) : paper.w;
  const height = mode === 'preview' ? Math.round(paper.h * previewScale) : paper.h;

  const renderSeed = Math.floor(seed * 1000) + width * 13 + height * 7;
  const random = seededRandom(renderSeed >>> 0);

  const context = canvas.getContext('2d');
  if (!context) {
    throw new Error('Canvas context is unavailable');
  }

  if (mode === 'preview') {
    const dpr = window.devicePixelRatio || 1;
    canvas.width = Math.round(width * dpr);
    canvas.height = Math.round(height * dpr);
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;
    context.setTransform(dpr, 0, 0, dpr, 0, 0);
  } else {
    canvas.width = width;
    canvas.height = height;
    context.setTransform(1, 0, 0, 1, 0, 0);
  }

  let bgImage: HTMLImageElement | null = null;
  const bgConfig = PAPER_BACKGROUNDS[safeState.paperBackground];
  if (bgConfig && bgConfig.type === 'image') {
    try {
      bgImage = await preloadBackgroundImage(safeState.paperBackground);
    } catch (error) {
      console.error('Background image load error:', error);
    }
  }

  const drawRect = drawPaperBackground(context, safeState.paperBackground, width, height, bgImage);
  await ensureFontReady(safeState.fontFamily, targetFontSize);

  drawTextContent({
    drawCtx: context,
    state: safeState,
    width,
    height,
    drawRect,
    fontSize: targetFontSize,
    random,
  });

  return { width, height };
};

export const renderPreviewCanvas = async (canvas: HTMLCanvasElement, state: HandwritingState, seed: number) =>
  renderInternal({
    canvas,
    state,
    seed,
    mode: 'preview',
  });

export const renderExportCanvas = async (canvas: HTMLCanvasElement, state: HandwritingState, seed: number) =>
  renderInternal({
    canvas,
    state,
    seed,
    mode: 'export',
  });

export const getExportDataUrl = async (state: HandwritingState, seed: number) => {
  const exportCanvas = document.createElement('canvas');
  await renderExportCanvas(exportCanvas, state, seed);
  return exportCanvas.toDataURL('image/png');
};

export const downloadDataUrl = (dataUrl: string, filename: string) => {
  const link = document.createElement('a');
  link.href = dataUrl;
  link.download = filename;
  link.click();
};

export const getExportFilename = (state: HandwritingState) => {
  const paperType = state.paperType || DEFAULT_STATE.paperType;
  return `handwriting-${paperType}-${Date.now()}.png`;
};

export const downloadExportImage = async (state: HandwritingState, seed: number) => {
  const dataUrl = await getExportDataUrl(state, seed);
  downloadDataUrl(dataUrl, getExportFilename(state));
  return dataUrl;
};

export const printExportImage = async (state: HandwritingState, seed: number) => {
  const dataUrl = await getExportDataUrl(state, seed);
  const printWindow = window.open('', '_blank');

  if (!printWindow) {
    throw new Error('无法打开打印窗口，请检查浏览器弹窗设置');
  }

  printWindow.document.open();
  printWindow.document.write(`
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
      <meta charset="UTF-8" />
      <title>打印手写体</title>
      <style>
        html, body {
          margin: 0;
          padding: 0;
          background: #fff;
        }
        body {
          display: flex;
          justify-content: center;
          align-items: flex-start;
        }
        img {
          width: 100%;
          max-width: 100%;
          height: auto;
          display: block;
        }
        @media print {
          @page { margin: 0; size: auto; }
          body { padding: 0; }
        }
      </style>
    </head>
    <body>
      <img src="${dataUrl}" alt="打印手写体" />
    </body>
    </html>
  `);
  printWindow.document.close();

  printWindow.onload = () => {
    printWindow.focus();
    printWindow.print();
  };
};

export const getPreviewDataUrl = (canvas: HTMLCanvasElement | null) => {
  if (!canvas) {
    return null;
  }
  return canvas.toDataURL('image/png');
};
