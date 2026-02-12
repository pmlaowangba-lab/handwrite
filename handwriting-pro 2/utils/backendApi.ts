import { HandwritingState } from '../types';

export interface BackendRenderTask {
  task_id: string;
  status: 'pending' | 'running' | 'success' | 'failed' | string;
  input_json: Record<string, unknown>;
  file_url: string | null;
  error_message: string | null;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
}

type TaskProgressCallback = (message: string) => void;

const rawBaseUrl = import.meta.env.VITE_BACKEND_BASE_URL || 'http://127.0.0.1:9000';
const BACKEND_BASE_URL = rawBaseUrl.replace(/\/$/, '');

const resolveBackendUrl = (path: string) =>
  path.startsWith('http') ? path : `${BACKEND_BASE_URL}${path.startsWith('/') ? '' : '/'}${path}`;

const parseFilenameFromContentDisposition = (headerValue: string | null): string | null => {
  if (!headerValue) {
    return null;
  }
  const utf8Match = headerValue.match(/filename\*=UTF-8''([^;]+)/i);
  if (utf8Match?.[1]) {
    return decodeURIComponent(utf8Match[1]);
  }
  const asciiMatch = headerValue.match(/filename="?([^"]+)"?/i);
  if (asciiMatch?.[1]) {
    return asciiMatch[1];
  }
  return null;
};

const downloadBlob = (blob: Blob, filename: string) => {
  const objectUrl = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = objectUrl;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(objectUrl);
};

const blobToDataUrl = (blob: Blob) =>
  new Promise<string>((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result));
    reader.onerror = () => reject(new Error('无法读取导出文件'));
    reader.readAsDataURL(blob);
  });

const buildSubmitPayload = (state: HandwritingState, seed: number) => ({
  text: state.text,
  font_family: state.fontFamily,
  paper_type: state.paperType,
  paper_background: state.paperBackground,
  position_jitter: state.positionJitter,
  font_size: state.fontSize,
  line_height: state.lineHeight,
  scratch_rate: state.scratchRate,
  weight_variation: state.weightVariation,
  note_sloppiness: state.noteSloppiness,
  render_scale: 0.5,
  random_seed: Math.floor(seed * 100000),
});

export const submitRenderTask = async (state: HandwritingState, seed: number) => {
  const response = await fetch(resolveBackendUrl('/api/v1/render/tasks'), {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(buildSubmitPayload(state, seed)),
  });

  if (!response.ok) {
    const bodyText = await response.text();
    throw new Error(`提交渲染任务失败（${response.status}）：${bodyText || response.statusText}`);
  }

  const data = (await response.json()) as { task_id: string; status: string };
  return data.task_id;
};

export const getRenderTask = async (taskId: string): Promise<BackendRenderTask> => {
  const response = await fetch(resolveBackendUrl(`/api/v1/render/tasks/${taskId}`));
  if (!response.ok) {
    const bodyText = await response.text();
    throw new Error(`查询任务失败（${response.status}）：${bodyText || response.statusText}`);
  }
  return (await response.json()) as BackendRenderTask;
};

export const waitForRenderTask = async (
  taskId: string,
  onProgress?: TaskProgressCallback,
  timeoutMs = 120000,
  intervalMs = 1200,
) => {
  const start = Date.now();

  while (Date.now() - start < timeoutMs) {
    const task = await getRenderTask(taskId);
    if (task.status === 'success') {
      onProgress?.('渲染完成');
      return task;
    }
    if (task.status === 'failed') {
      throw new Error(task.error_message || '后端渲染失败');
    }

    onProgress?.(task.status === 'running' ? '后端渲染中...' : '任务排队中...');
    await new Promise((resolve) => window.setTimeout(resolve, intervalMs));
  }

  throw new Error('渲染超时，请稍后重试');
};

const fetchRenderedFile = async (task: BackendRenderTask) => {
  if (!task.file_url) {
    throw new Error('任务已完成但未返回文件地址');
  }
  const url = resolveBackendUrl(task.file_url);
  const response = await fetch(url);
  if (!response.ok) {
    const bodyText = await response.text();
    throw new Error(`下载渲染结果失败（${response.status}）：${bodyText || response.statusText}`);
  }

  const blob = await response.blob();
  const headerFilename = parseFilenameFromContentDisposition(response.headers.get('content-disposition'));
  const fallbackName = `${task.task_id}.png`;

  return {
    blob,
    filename: headerFilename || fallbackName,
  };
};

export const downloadRenderedTask = async (task: BackendRenderTask) => {
  const { blob, filename } = await fetchRenderedFile(task);
  downloadBlob(blob, filename);
};

export const printRenderedTask = async (task: BackendRenderTask) => {
  const { blob } = await fetchRenderedFile(task);
  const dataUrl = await blobToDataUrl(blob);
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
