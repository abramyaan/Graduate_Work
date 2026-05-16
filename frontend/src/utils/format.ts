/**
 * Форматирует дату в читаемый формат
 */
export const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleString('ru-RU', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

/**
 * Форматирует дату в короткий формат
 */
export const formatDateShort = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleDateString('ru-RU');
};

/**
 * Форматирует число до указанного количества знаков после запятой
 */
export const formatScore = (score: number, decimals: number = 2): string => {
  return score.toFixed(decimals);
};

/**
 * Возвращает цветовой класс для балла
 */
export const getScoreColorClass = (score: number): string => {
  if (score >= 75) return 'text-green-600';
  if (score >= 50) return 'text-yellow-600';
  return 'text-red-600';
};

/**
 * Возвращает цветовой класс фона для балла
 */
export const getScoreBgClass = (score: number): string => {
  if (score >= 75) return 'bg-green-50';
  if (score >= 50) return 'bg-yellow-50';
  return 'bg-red-50';
};
