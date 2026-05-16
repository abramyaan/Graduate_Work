import React from 'react';

interface ScoreCardProps {
  title: string;
  score: number;
  maxScore?: number;
  color?: 'green' | 'yellow' | 'red' | 'blue';
}

const ScoreCard: React.FC<ScoreCardProps> = ({
  title,
  score,
  maxScore = 100,
  color,
}) => {
  const getColor = () => {
    if (color) {
      const colors = {
        green: 'bg-green-500',
        yellow: 'bg-yellow-500',
        red: 'bg-red-500',
        blue: 'bg-blue-500',
      };
      return colors[color];
    }

    if (score >= 75) return 'bg-green-500';
    if (score >= 50) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const percentage = (score / maxScore) * 100;

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-sm font-medium text-gray-600 mb-2">{title}</h3>
      <div className="flex items-center justify-between mb-2">
        <span className="text-3xl font-bold text-gray-900">
          {score.toFixed(2)}
        </span>
        <span className="text-sm text-gray-500">/ {maxScore}</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className={`${getColor()} h-2 rounded-full transition-all duration-300`}
          style={{ width: `${percentage}%` }}
        ></div>
      </div>
    </div>
  );
};

export default ScoreCard;
