/**
 * Скачивает blob как файл
 */
export const downloadBlob = (
  blob: Blob,
  filename: string
): void => {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};

/**
 * Скачивает данные как JSON файл
 */
export const downloadJSON = (data: any, filename: string): void => {
  const json = JSON.stringify(data, null, 2);
  const blob = new Blob([json], { type: 'application/json' });
  downloadBlob(blob, filename);
};

/**
 * Открывает файл в новом окне
 */
export const openFile = (url: string): void => {
  window.open(url, '_blank', 'noopener,noreferrer');
};
