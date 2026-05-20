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
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg m-6">
          {error || 'Данные не найдены'}
        </div>
      </Layout>
    );
  }

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
    // Используем w-full, p-6 и убираем любые центрирующие контейнеры, чтобы занять 100% ширины
    <div className="w-full min-h-screen bg-gray-50 p-6">
      <button
        onClick={() => navigate(-1)}
        className="text-blue-600 hover:text-blue-800 mb-6 flex items-center font-medium transition-colors"
      >
        ← Назад к списку
      </button>

      {/* Основная сетка: Две огромные колонки (Левая для инфы, Правая для графиков) */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 items-start w-full mb-6">
        
        {/* ================= ЛЕВАЯ СТОРОНА ================= */}
        <div className="space-y-6 w-full flex flex-col h-full justify-between">
          {/* Блок 1: Общие данные кандидата */}
          <div className="bg-white shadow-lg rounded-xl p-8 flex-1 border border-gray-100">
            <div className="flex flex-col sm:flex-row justify-between items-start gap-6 mb-6">
              <div>
                <h1 className="text-4xl font-extrabold text-gray-900 mb-4 tracking-tight">
                  {evaluation.candidate.full_name}
                </h1>
                <div className="space-y-2 text-base text-gray-600">
                  <p><span className="font-semibold text-gray-700">Email:</span> {evaluation.candidate.email}</p>
                  <p><span className="font-semibold text-gray-700">Телефон:</span> {evaluation.candidate.phone}</p>
                  <p><span className="font-semibold text-gray-700">Вакансия:</span> <span className="text-blue-600 font-medium">{evaluation.vacancy.title}</span></p>
                  <p><span className="font-semibold text-gray-700">Оценено:</span> {new Date(evaluation.evaluated_at).toLocaleString('ru-RU')}</p>
                  <p><span className="font-semibold text-gray-700">Оценщик:</span> {evaluation.evaluator_name}</p>
                </div>
              </div>
              <div className="text-left sm:text-right bg-gray-50 p-6 rounded-xl border border-gray-100 min-w-[200px]">
                <div className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-1">Общий балл</div>
                <div
                  className={`text-6xl font-black ${
                    evaluation.overall_score >= 75
                      ? 'text-green-600'
                      : evaluation.overall_score >= 50
                      ? 'text-yellow-600'
                      : 'text-red-600'
                  }`}
                >
                  {evaluation.overall_score.toFixed(2)}
                </div>
                <div className="mt-4">
                  <span
                    className={`px-4 py-1.5 text-sm font-bold rounded-full text-white inline-block shadow-sm ${getScoreBadgeColor(
                      evaluation.overall_score
                    )}`}
                  >
                    {evaluation.recommendation}
                  </span>
                </div>
              </div>
            </div>

            {evaluation.resume_url && (
              <div className="mt-6 pt-4 border-t border-gray-100">
                <a
                  href={evaluation.resume_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-xl text-sm font-semibold shadow-md hover:shadow-lg transition-all"
                >
                  📄 Скачать оригинальное резюме
                </a>
              </div>
            )}
          </div>

          {/* Блок 2: Детализация по категориям */}
          <div className="bg-white shadow-lg rounded-xl p-8 flex-1 border border-gray-100">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 tracking-tight">
              Детализация оценки по критериям
            </h2>
            <div className="space-y-6">
              {evaluation.category_scores.map((cat) => (
                <div
                  key={cat.category_name}
                  className="border border-gray-100 bg-gray-50/50 rounded-xl p-5 hover:border-blue-200 transition-colors"
                >
                  <div className="flex justify-between items-center mb-3">
                    <h3 className="text-lg font-bold text-gray-800">{cat.category_name}</h3>
                    <span className="text-sm font-semibold bg-gray-200 text-gray-700 px-2.5 py-1 rounded-md">
                      Вес: {(cat.weight * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="flex-1 bg-gray-200 rounded-full h-4 shadow-inner">
                      <div
                        className={`h-4 rounded-full transition-all duration-500 shadow ${
                          cat.score >= 75
                            ? 'bg-green-500'
                            : cat.score >= 50
                            ? 'bg-yellow-500'
                            : 'bg-red-500'
                        }`}
                        style={{ width: `${cat.score}%` }}
                      ></div>
                    </div>
                    <span className="text-xl font-black text-gray-900 min-w-[60px] text-right">
                      {cat.score.toFixed(2)}
                    </span>
                  </div>
                  <div className="mt-2 text-sm text-gray-500 font-medium">
                    Взвешенный вклад в общую оценку: <span className="text-gray-800 font-bold">{cat.weighted_score.toFixed(2)}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* ================= ПРАВАЯ СТОРОНА (ГРАФИКИ) ================= */}
        <div className="space-y-6 w-full">
          {/* График 1: Столбчатая диаграмма */}
          <div className="bg-white shadow-lg rounded-xl p-8 border border-gray-100">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 tracking-tight">
              Баллы по категориям (Диаграмма)
            </h2>
            <div className="w-full h-[350px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={barChartData} margin={{ bottom: 40 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="category" angle={-25} textAnchor="end" height={80} tick={{ fill: '#4b5563', fontSize: 13 }} />
                  <YAxis domain={[0, 100]} tick={{ fill: '#4b5563' }} />
                  <Tooltip cursor={{ fill: '#f3f4f6' }} />
                  <Legend wrapperStyle={{ pt: 20 }} />
                  <Bar dataKey="score" fill="#3b82f6" radius={[4, 4, 0, 0]} name="Выставленный балл" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* График 2: Радарный профиль */}
          <div className="bg-white shadow-lg rounded-xl p-8 border border-gray-100">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 tracking-tight">
              Радарный профиль компетенций
            </h2>
            <div className="w-full h-[350px]">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart data={radarChartData}>
                  <PolarGrid stroke="#e5e7eb" />
                  <PolarAngleAxis dataKey="category" tick={{ fill: '#4b5563', fontSize: 13 }} />
                  <PolarRadiusAxis angle={90} domain={[0, 100]} />
                  <Radar
                    name="Оценка"
                    dataKey="value"
                    stroke="#2563eb"
                    fill="#3b82f6"
                    fillOpacity={0.4}
                  />
                  <Tooltip />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

      </div>

      {/* ================= НИЖНЯЯ СТРОКА НА ВСЮ ШИРИНУ ================= */}
      {evaluation.matching_analysis && (
        <div className="bg-white shadow-lg rounded-xl p-8 w-full border border-gray-100">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 tracking-tight">
            Интеллектуальный анализ соответствия кандидата
          </h2>

          {/* Итоговое резюме AI */}
          <div className="mb-8 p-6 bg-blue-50/70 border-l-4 border-blue-600 rounded-xl">
            <h3 className="text-lg font-bold text-blue-900 mb-2">Итоговый AI-вывод модели</h3>
            <p className="text-gray-700 text-base leading-relaxed font-medium">
              {evaluation.matching_analysis.summary}
            </p>
          </div>

          {/* Сетка навыков */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
            {/* Совпадающие навыки */}
            <div className="bg-green-50/30 p-6 rounded-xl border border-green-100">
              <h3 className="text-lg font-bold text-green-900 mb-4 flex items-center gap-2">
                🟢 Совпадающие ключевые навыки ({evaluation.matching_analysis.matched_skills.length})
              </h3>
              <div className="flex flex-wrap gap-2.5">
                {evaluation.matching_analysis.matched_skills.length > 0 ? (
                  evaluation.matching_analysis.matched_skills.map((skill, idx) => (
                    <span
                      key={idx}
                      className="px-3.5 py-1.5 bg-green-100 text-green-900 text-sm font-semibold rounded-lg border border-green-200 shadow-sm"
                    >
                      {skill}
                    </span>
                    ))
                ) : (
                  <p className="text-gray-500 text-sm italic">Пересечений по хард-скиллам не обнаружено</p>
                )}
              </div>
            </div>

            {/* Отсутствующие навыки */}
            <div className="bg-red-50/30 p-6 rounded-xl border border-red-100">
              <h3 className="text-lg font-bold text-red-900 mb-4 flex items-center gap-2">
                🔴 Отсутствующие требования вакансии ({evaluation.matching_analysis.missing_skills.length})
              </h3>
              <div className="flex flex-wrap gap-2.5">
                {evaluation.matching_analysis.missing_skills.length > 0 ? (
                  evaluation.matching_analysis.missing_skills.map((skill, idx) => (
                    <span
                      key={idx}
                      className="px-3.5 py-1.5 bg-red-100 text-red-900 text-sm font-semibold rounded-lg border border-red-200 shadow-sm"
                    >
                      {skill}
                    </span>
                  ))
                ) : (
                  <p className="text-gray-500 text-sm italic">Идеально! Все ключевые требования найдены в резюме</p>
                )}
              </div>
            </div>
          </div>

          {/* Релевантные выдержки */}
          {evaluation.matching_analysis.resume_highlights.length > 0 && (
            <div className="pt-4 border-t border-gray-100">
              <h3 className="text-lg font-bold text-gray-900 mb-4">
                Критические маркеры и подтверждения из опыта работы
              </h3>
              <div className="space-y-4">
                {evaluation.matching_analysis.resume_highlights.map((highlight, idx) => (
                  <div
                    key={idx}
                    className="p-4 bg-gray-50 border border-gray-200 rounded-xl hover:bg-gray-100/70 transition-colors"
                  >
                    <p className="text-gray-700 text-sm leading-relaxed flex items-start">
                      <span className="inline-flex items-center justify-center bg-blue-100 text-blue-700 font-bold rounded-lg h-6 w-6 text-xs mr-3 flex-shrink-0 mt-0.5">
                        {idx + 1}
                      </span>
                      <span className="font-medium">{highlight}</span>
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default CandidateDetail;