import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from 'recharts';
import Layout from '../components/Layout';
import LoadingSpinner from '../components/LoadingSpinner';
import { evaluationsApi } from '../api/evaluations';
import { DetailedEvaluation } from '../types';

const CandidateDetail: React.FC = () => {
  const { evaluationId } = useParams<{ evaluationId: string }>();
  const navigate = useNavigate();
  const [evaluation, setEvaluation] = useState<DetailedEvaluation | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (evaluationId) {
      loadEvaluation(parseInt(evaluationId));
    }
  }, [evaluationId]);

  const loadEvaluation = async (id: number) => {
    try {
      const data = await evaluationsApi.getById(id);
      // Преобразуем overall_score из строки в число
      const normalizedData = {
        ...data,
        overall_score: Number(data.overall_score),
        category_scores: data.category_scores.map(cs => ({
          ...cs,
          score: Number(cs.score),
          weight: Number(cs.weight),
          weighted_score: Number(cs.weighted_score),
        })),
      };
      setEvaluation(normalizedData);
    } catch (err: any) {
      setError('Ошибка загрузки данных: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const getScoreBadgeColor = (score: number): string => {
    if (score >= 75) return 'bg-green-500';
    if (score >= 50) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  if (loading) {
    return (
      <Layout>
        <LoadingSpinner />
      </Layout>
    );
  }

  if (error || !evaluation) {
    return (
      <Layout>
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error || 'Данные не найдены'}
        </div>
      </Layout>
    );
  }

  // Данные для графиков
  const barChartData = evaluation.category_scores.map((cat) => ({
    category: cat.category_name,
    score: cat.score,
    weight: cat.weight * 100,
  }));

  const radarChartData = evaluation.category_scores.map((cat) => ({
    category: cat.category_name,
    value: cat.score,
  }));

  return (
    <Layout>
      <div className="px-4 sm:px-0">
        <button
          onClick={() => navigate(-1)}
          className="text-blue-600 hover:text-blue-800 mb-4 flex items-center"
        >
          ← Назад
        </button>

        {/* Заголовок и общая информация */}
        <div className="bg-white shadow-md rounded-lg p-6 mb-6">
          <div className="flex justify-between items-start mb-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                {evaluation.candidate.full_name}
              </h1>
              <div className="space-y-1 text-gray-600">
                <p>Email: {evaluation.candidate.email}</p>
                <p>Телефон: {evaluation.candidate.phone}</p>
                <p>Вакансия: {evaluation.vacancy.title}</p>
                <p>Оценено: {new Date(evaluation.evaluated_at).toLocaleString('ru-RU')}</p>
                <p>Оценщик: {evaluation.evaluator_name}</p>
              </div>
            </div>
            <div className="text-right">
              <div className="text-sm text-gray-500 mb-2">Общий балл</div>
              <div
                className={`text-5xl font-bold ${
                  evaluation.overall_score >= 75
                    ? 'text-green-600'
                    : evaluation.overall_score >= 50
                    ? 'text-yellow-600'
                    : 'text-red-600'
                }`}
              >
                {evaluation.overall_score.toFixed(2)}
              </div>
              <div className="mt-3">
                <span
                  className={`px-3 py-1 text-sm font-semibold rounded-full text-white ${getScoreBadgeColor(
                    evaluation.overall_score
                  )}`}
                >
                  {evaluation.recommendation}
                </span>
              </div>
            </div>
          </div>

          {evaluation.resume_url && (
            <div className="mt-4">
              <a
                href={evaluation.resume_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium"
              >
                📄 Скачать резюме
              </a>
            </div>
          )}
        </div>

        {/* Детализация по категориям */}
        <div className="bg-white shadow-md rounded-lg p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Детализация оценки по категориям
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {evaluation.category_scores.map((cat) => (
              <div
                key={cat.category_name}
                className="border border-gray-200 rounded-lg p-4"
              >
                <div className="flex justify-between items-center mb-2">
                  <h3 className="font-medium text-gray-900">{cat.category_name}</h3>
                  <span className="text-sm text-gray-500">Вес: {(cat.weight * 100).toFixed(0)}%</span>
                </div>
                <div className="flex items-center">
                  <div className="flex-1 bg-gray-200 rounded-full h-3 mr-3">
                    <div
                      className={`h-3 rounded-full ${
                        cat.score >= 75
                          ? 'bg-green-500'
                          : cat.score >= 50
                          ? 'bg-yellow-500'
                          : 'bg-red-500'
                      }`}
                      style={{ width: `${cat.score}%` }}
                    ></div>
                  </div>
                  <span className="text-lg font-bold text-gray-900">
                    {cat.score.toFixed(2)}
                  </span>
                </div>
                <div className="mt-1 text-sm text-gray-600">
                  Взвешенный балл: {cat.weighted_score.toFixed(2)}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Графики */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Столбчатая диаграмма */}
          <div className="bg-white shadow-md rounded-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Баллы по категориям
            </h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={barChartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="category" angle={-45} textAnchor="end" height={100} />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Legend />
                <Bar dataKey="score" fill="#3b82f6" name="Балл" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Радарная диаграмма */}
          <div className="bg-white shadow-md rounded-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Профиль кандидата
            </h2>
            <ResponsiveContainer width="100%" height={300}>
              <RadarChart data={radarChartData}>
                <PolarGrid />
                <PolarAngleAxis dataKey="category" />
                <PolarRadiusAxis angle={90} domain={[0, 100]} />
                <Radar
                  name="Оценка"
                  dataKey="value"
                  stroke="#3b82f6"
                  fill="#3b82f6"
                  fillOpacity={0.6}
                />
                <Tooltip />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default CandidateDetail;
