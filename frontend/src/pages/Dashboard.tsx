import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
} from 'recharts';
import Layout from '../components/Layout';
import LoadingSpinner from '../components/LoadingSpinner';
import { useToast } from '../context/ToastContext';
import { vacanciesApi } from '../api/vacancies';
import { evaluationsApi } from '../api/evaluations';
import { resumesApi } from '../api/resumes';
import { statisticsApi, DashboardStats, VacancyStatsItem, RecentEvaluationItem } from '../api/statistics';
import { Vacancy } from '../types';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { showSuccess, showError, showInfo } = useToast();
  const [vacancies, setVacancies] = useState<Vacancy[]>([]);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [topVacancies, setTopVacancies] = useState<VacancyStatsItem[]>([]);
  const [recentEvaluations, setRecentEvaluations] = useState<RecentEvaluationItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [runningEvaluation, setRunningEvaluation] = useState<number | null>(null);

  useEffect(() => {
    loadAllData();
  }, []);

  const loadAllData = async () => {
    try {
      const [vacanciesData, statsData, topVacanciesData, recentData] = await Promise.all([
        vacanciesApi.getActive(),
        statisticsApi.getDashboardStats(),
        statisticsApi.getTopVacancies(5),
        statisticsApi.getRecentEvaluations(5),
      ]);

      setVacancies(vacanciesData);
      setStats(statsData);
      setTopVacancies(topVacanciesData);
      setRecentEvaluations(recentData);
    } catch (err: any) {
      setError('Ошибка загрузки данных: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleRunEvaluation = async (vacancyId: number) => {
    setRunningEvaluation(vacancyId);
    showInfo('Запуск оценки резюме...');
    try {
      const resumes = await resumesApi.getByVacancy(vacancyId);

      if (resumes.length === 0) {
        showError('Нет резюме для оценки по этой вакансии');
        setRunningEvaluation(null);
        return;
      }

      const resumeIds = resumes.map((r) => r.resume_id);

      const result = await evaluationsApi.evaluate({
        vacancy_id: vacancyId,
        resume_ids: resumeIds,
      });

      showSuccess(`Оценка завершена! Обработано резюме: ${result.count}`);
      navigate(`/results/${vacancyId}`);
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message;
      showError('Ошибка запуска оценки: ' + errorMessage);
    } finally {
      setRunningEvaluation(null);
    }
  };

  const handleViewResults = (vacancyId: number) => {
    navigate(`/results/${vacancyId}`);
  };

  if (loading) {
    return (
      <Layout>
        <LoadingSpinner />
      </Layout>
    );
  }

  // Данные для круговой диаграммы
  const pieData = stats
    ? [
        { name: 'Высокий (≥75)', value: stats.high_score_count, color: '#10b981' },
        { name: 'Средний (50-74)', value: stats.medium_score_count, color: '#f59e0b' },
        { name: 'Низкий (<50)', value: stats.low_score_count, color: '#ef4444' },
      ]
    : [];

  // Данные для столбчатой диаграммы топ вакансий
  const barData = topVacancies.map((v) => ({
    name: v.title.length > 20 ? v.title.substring(0, 20) + '...' : v.title,
    resumes: v.resume_count,
    avg_score: v.avg_score,
  }));

  const getRecommendationColor = (recommendation: string) => {
    if (recommendation.includes('немедленно') || recommendation.includes('Пригласить')) {
      return 'bg-green-100 text-green-800';
    }
    if (recommendation.includes('Отложить')) {
      return 'bg-yellow-100 text-yellow-800';
    }
    return 'bg-red-100 text-red-800';
  };

  return (
    <Layout>
      <div className="px-4 sm:px-0">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Дашборд</h1>
          <div className="flex space-x-3">
            <button
              onClick={() => navigate('/candidates')}
              className="bg-purple-500 hover:bg-purple-600 text-white px-6 py-2 rounded-lg font-medium"
            >
              Кандидаты
            </button>
            <button
              onClick={() => navigate('/vacancies/create')}
              className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-lg font-medium"
            >
              + Создать вакансию
            </button>
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
            {error}
          </div>
        )}

        {/* Статистические карточки */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <div className="bg-white shadow-md rounded-lg p-6">
              <div className="text-sm font-medium text-gray-500 mb-1">Всего вакансий</div>
              <div className="text-3xl font-bold text-gray-900">{stats.total_vacancies}</div>
              <div className="text-sm text-green-600 mt-1">
                {stats.active_vacancies} активных
              </div>
            </div>

            <div className="bg-white shadow-md rounded-lg p-6">
              <div className="text-sm font-medium text-gray-500 mb-1">Кандидаты</div>
              <div className="text-3xl font-bold text-gray-900">{stats.total_candidates}</div>
              <div className="text-sm text-gray-600 mt-1">
                {stats.total_resumes} резюме
              </div>
            </div>

            <div className="bg-white shadow-md rounded-lg p-6">
              <div className="text-sm font-medium text-gray-500 mb-1">Оценок проведено</div>
              <div className="text-3xl font-bold text-gray-900">{stats.total_evaluations}</div>
            </div>

            <div className="bg-white shadow-md rounded-lg p-6">
              <div className="text-sm font-medium text-gray-500 mb-1">Средний балл</div>
              <div className="text-3xl font-bold text-gray-900">
                {stats.avg_score.toFixed(1)}
              </div>
              <div className="text-sm text-gray-600 mt-1">из 100</div>
            </div>
          </div>
        )}

        {/* Графики */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Круговая диаграмма распределения */}
          <div className="bg-white shadow-md rounded-lg p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">
              Распределение кандидатов по баллам
            </h2>
            {pieData.length > 0 && pieData.some((d) => d.value > 0) ? (
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-64 flex items-center justify-center text-gray-500">
                Нет данных для отображения
              </div>
            )}
          </div>

          {/* Столбчатая диаграмма топ вакансий */}
          <div className="bg-white shadow-md rounded-lg p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">
              Топ вакансий по откликам
            </h2>
            {barData.length > 0 ? (
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={barData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="resumes" fill="#3b82f6" name="Резюме" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-64 flex items-center justify-center text-gray-500">
                Нет данных для отображения
              </div>
            )}
          </div>
        </div>

        {/* Последние оценки */}
        {recentEvaluations.length > 0 && (
          <div className="bg-white shadow-md rounded-lg overflow-hidden mb-6">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-800">Последние оценки</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Кандидат
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Вакансия
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Балл
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Рекомендация
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Дата
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {recentEvaluations.map((evaluation) => (
                    <tr
                      key={evaluation.result_id}
                      className="hover:bg-gray-50 cursor-pointer"
                      onClick={() => navigate(`/candidate/${evaluation.result_id}`)}
                    >
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {evaluation.candidate_name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {evaluation.vacancy_title}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-gray-900">
                        {evaluation.overall_score.toFixed(2)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span
                          className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getRecommendationColor(
                            evaluation.recommendation
                          )}`}
                        >
                          {evaluation.recommendation}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(evaluation.analysis_date).toLocaleDateString('ru-RU')}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Активные вакансии */}
        <div className="bg-white shadow-md rounded-lg overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-800">Активные вакансии</h2>
          </div>

          {vacancies.length === 0 ? (
            <div className="px-6 py-8 text-center text-gray-500">
              Нет активных вакансий
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {vacancies.map((vacancy) => (
                <div
                  key={vacancy.vacancy_id}
                  className="px-6 py-4 hover:bg-gray-50 transition-colors"
                >
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">
                        {vacancy.title}
                      </h3>
                      <p className="text-gray-600 text-sm mb-3 line-clamp-2">
                        {vacancy.description}
                      </p>
                      {vacancy.specialization_name && (
                        <div className="mb-3">
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                            {vacancy.specialization_name}
                          </span>
                        </div>
                      )}
                      <div className="text-sm text-gray-500">
                        Создана: {new Date(vacancy.created_at).toLocaleDateString('ru-RU')}
                      </div>
                    </div>
                    <div className="ml-4 flex flex-col space-y-2">
                      <button
                        onClick={() => navigate(`/vacancies/edit/${vacancy.vacancy_id}`)}
                        className="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap"
                      >
                        Редактировать
                      </button>
                      <button
                        onClick={() => navigate(`/resumes/upload/${vacancy.vacancy_id}`)}
                        className="bg-purple-500 hover:bg-purple-600 text-white px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap"
                      >
                        Загрузить резюме
                      </button>
                      <button
                        onClick={() => handleRunEvaluation(vacancy.vacancy_id)}
                        disabled={runningEvaluation === vacancy.vacancy_id}
                        className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
                      >
                        {runningEvaluation === vacancy.vacancy_id ? 'Оценка...' : 'Запустить оценку'}
                      </button>
                      <button
                        onClick={() => handleViewResults(vacancy.vacancy_id)}
                        className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap"
                      >
                        Результаты
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default Dashboard;
