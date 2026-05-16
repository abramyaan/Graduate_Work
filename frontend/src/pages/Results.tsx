import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import LoadingSpinner from '../components/LoadingSpinner';
import { evaluationsApi } from '../api/evaluations';
import { vacanciesApi } from '../api/vacancies';
import { EvaluationResult, Vacancy } from '../types';

const Results: React.FC = () => {
  const { vacancyId } = useParams<{ vacancyId: string }>();
  const navigate = useNavigate();
  const [results, setResults] = useState<EvaluationResult[]>([]);
  const [vacancy, setVacancy] = useState<Vacancy | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [exporting, setExporting] = useState<'pdf' | 'excel' | null>(null);

  useEffect(() => {
    if (vacancyId) {
      loadData(parseInt(vacancyId));
    }
  }, [vacancyId]);

  const loadData = async (id: number) => {
    try {
      const [resultsData, vacancyData] = await Promise.all([
        evaluationsApi.getByVacancy(id),
        vacanciesApi.getById(id),
      ]);
      setResults(resultsData);
      setVacancy(vacancyData);
    } catch (err: any) {
      setError('Ошибка загрузки данных: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score: number): string => {
    if (score >= 75) return 'bg-green-50 hover:bg-green-100';
    if (score >= 50) return 'bg-yellow-50 hover:bg-yellow-100';
    return 'bg-red-50 hover:bg-red-100';
  };

  const getRecommendationBadge = (recommendation: string): string => {
    if (recommendation.includes('немедленно') || recommendation.includes('Пригласить')) {
      return 'bg-green-100 text-green-800';
    }
    if (recommendation.includes('Отложить')) {
      return 'bg-yellow-100 text-yellow-800';
    }
    return 'bg-red-100 text-red-800';
  };

  const handleExport = async (format: 'pdf' | 'excel') => {
    if (!vacancyId) return;

    setExporting(format);
    try {
      const blob = await evaluationsApi.exportResults(parseInt(vacancyId), format);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `results_vacancy_${vacancyId}.${format === 'pdf' ? 'pdf' : 'xlsx'}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err: any) {
      alert('Ошибка экспорта: ' + (err.response?.data?.detail || err.message));
    } finally {
      setExporting(null);
    }
  };

  const handleViewDetails = (evaluationId: number) => {
    navigate(`/candidate/${evaluationId}`);
  };

  if (loading) {
    return (
      <Layout>
        <LoadingSpinner />
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="px-4 sm:px-0">
        <div className="mb-6">
          <button
            onClick={() => navigate('/dashboard')}
            className="text-blue-600 hover:text-blue-800 mb-4 flex items-center"
          >
            ← Назад к дашборду
          </button>
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                Результаты оценки
              </h1>
              {vacancy && (
                <p className="text-lg text-gray-600">Вакансия: {vacancy.title}</p>
              )}
            </div>
            <div className="flex space-x-3">
              <button
                onClick={() => handleExport('pdf')}
                disabled={exporting !== null}
                className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg text-sm font-medium disabled:opacity-50"
              >
                {exporting === 'pdf' ? 'Экспорт...' : 'Экспорт PDF'}
              </button>
              <button
                onClick={() => handleExport('excel')}
                disabled={exporting !== null}
                className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg text-sm font-medium disabled:opacity-50"
              >
                {exporting === 'excel' ? 'Экспорт...' : 'Экспорт Excel'}
              </button>
            </div>
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
            {error}
          </div>
        )}

        {results.length === 0 ? (
          <div className="bg-white shadow-md rounded-lg px-6 py-8 text-center text-gray-500">
            Нет результатов оценки для данной вакансии
          </div>
        ) : (
          <div className="bg-white shadow-md rounded-lg overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      ФИО
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Общий балл
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Навыки
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Опыт
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Структура
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      ATS
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Рекомендация
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Действия
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {results.map((result) => (
                    <tr
                      key={result.id}
                      className={`${getScoreColor(result.overall_score)} transition-colors cursor-pointer`}
                      onClick={() => handleViewDetails(result.id)}
                    >
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {result.candidate.full_name}
                        </div>
                        <div className="text-sm text-gray-500">
                          {result.candidate.email}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-lg font-bold text-gray-900">
                          {result.overall_score.toFixed(2)}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {result.skills_score.toFixed(2)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {result.experience_score.toFixed(2)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {result.structure_score.toFixed(2)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {result.ats_score.toFixed(2)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span
                          className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getRecommendationBadge(
                            result.recommendation
                          )}`}
                        >
                          {result.recommendation}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleViewDetails(result.id);
                          }}
                          className="text-blue-600 hover:text-blue-900 font-medium"
                        >
                          Подробнее
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default Results;
