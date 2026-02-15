(function (global) {
  const DEFAULT_BACKEND_BASE_URL = 'http://127.0.0.1:9000';

  function resolveBaseUrl(explicitBaseUrl) {
    const fromWindow = global.HW_BACKEND_BASE_URL;
    const fromStorage =
      typeof global.localStorage !== 'undefined'
        ? global.localStorage.getItem('HW_BACKEND_BASE_URL')
        : null;
    const base = explicitBaseUrl || fromWindow || fromStorage || DEFAULT_BACKEND_BASE_URL;
    return String(base).replace(/\/$/, '');
  }

  function sleep(ms) {
    return new Promise((resolve) => global.setTimeout(resolve, ms));
  }

  function parseFilename(contentDisposition) {
    if (!contentDisposition) return null;
    const utf8Match = contentDisposition.match(/filename\*=UTF-8''([^;]+)/i);
    if (utf8Match && utf8Match[1]) return decodeURIComponent(utf8Match[1]);
    const asciiMatch = contentDisposition.match(/filename="?([^"]+)"?/i);
    if (asciiMatch && asciiMatch[1]) return asciiMatch[1];
    return null;
  }

  function blobToDataUrl(blob) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = () => reject(new Error('读取文件失败'));
      reader.readAsDataURL(blob);
    });
  }

  function downloadBlob(blob, filename) {
    const objectUrl = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.download = filename;
    link.href = objectUrl;
    link.click();
    URL.revokeObjectURL(objectUrl);
  }

  function createHandwriteBackendClient(options) {
    const config = options || {};
    const backendBaseUrl = resolveBaseUrl(config.backendBaseUrl);
    const timeoutMs = config.timeoutMs || 120000;
    const pollIntervalMs = config.pollIntervalMs || 1200;

    function backendApiUrl(path) {
      if (path.startsWith('http')) return path;
      return backendBaseUrl + (path.startsWith('/') ? '' : '/') + path;
    }

    async function readErrorMessage(response, fallback) {
      try {
        const payload = await response.json();
        if (payload && typeof payload === 'object') {
          if (payload.detail) return String(payload.detail);
          if (payload.error) return String(payload.error);
          if (payload.message) return String(payload.message);
        }
      } catch (error) {
        return (await response.text()) || fallback;
      }
      return fallback;
    }

    async function submitRenderTask(payload) {
      const response = await fetch(backendApiUrl('/api/v1/render/tasks'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const text = await response.text();
        throw new Error(`提交渲染任务失败（${response.status}）：${text || response.statusText}`);
      }

      const result = await response.json();
      return result.task_id;
    }

    async function pollRenderTask(taskId, onProgress) {
      const start = Date.now();

      while (Date.now() - start < timeoutMs) {
        const response = await fetch(backendApiUrl(`/api/v1/render/tasks/${taskId}`));
        if (!response.ok) {
          const text = await response.text();
          throw new Error(`查询渲染任务失败（${response.status}）：${text || response.statusText}`);
        }

        const task = await response.json();
        if (task.status === 'success') {
          onProgress && onProgress('✅ 渲染完成');
          return task;
        }
        if (task.status === 'failed') {
          throw new Error(task.error_message || '后端渲染失败');
        }

        onProgress && onProgress(task.status === 'running' ? '⏳ 后端渲染中...' : '⏳ 任务排队中...');
        await sleep(pollIntervalMs);
      }

      throw new Error('渲染超时，请稍后重试');
    }

    async function fetchRenderedFile(task) {
      if (!task.file_url) {
        throw new Error('任务完成但未返回下载地址');
      }

      const response = await fetch(backendApiUrl(task.file_url));
      if (!response.ok) {
        const text = await response.text();
        throw new Error(`下载渲染结果失败（${response.status}）：${text || response.statusText}`);
      }

      const blob = await response.blob();
      const filename = parseFilename(response.headers.get('content-disposition')) || `${task.task_id}.png`;
      return { blob, filename, task };
    }

    async function runRenderTask(payload, onProgress) {
      const taskId = await submitRenderTask(payload);
      const task = await pollRenderTask(taskId, onProgress);
      return fetchRenderedFile(task);
    }

    async function polishNote(payload) {
      const response = await fetch(backendApiUrl('/api/v1/ai/polish-note'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const detail = await readErrorMessage(response, response.statusText);
        throw new Error(`AI 润色失败（${response.status}）：${detail}`);
      }

      return response.json();
    }

    return {
      backendApiUrl,
      submitRenderTask,
      pollRenderTask,
      fetchRenderedFile,
      runRenderTask,
      polishNote,
      blobToDataUrl,
      downloadBlob
    };
  }

  global.createHandwriteBackendClient = createHandwriteBackendClient;
})(window);
