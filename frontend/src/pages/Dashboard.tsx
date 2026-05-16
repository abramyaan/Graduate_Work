import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import LoadingSpinner from '../components/LoadingSpinner';
import { vacanciesApi } from '../api/vacancies';
import { evaluationsApi } from '../api/evaluations';
import { Vacancy } from '../types';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [vacancies, setVacancies] = useState<Vacancy[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [runningEvaluation, setRunningEvaluation] = useState<number | null>(null);

  useEffect(() => {
    loadVacancies();
  }, []);

  const loadVacancies = async () => {
    try {
      const data = await vacanciesApi.getActive();
      setVacancies(data);
    } catch (err: any) {
      setError('Ошибка загрузки вакансий: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleRunEvaluation = async (vacancyId: number) => {
    setRunningEvaluation(vacancyId);
    try {
      const result = await evaluationsApi.runEvaluation(vacancyId);
      alert(`Оценка завершена! Обработано резюме: ${result.count}`);
      navigate(`/results/${vacancyId}`);
    } catch (err: any) {
      alert('Ошибка запуска оценки: ' + (err.response?.data?.detail || err.message));
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

  return (
    <Layout>
      <div className="px-4 sm:px-0">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Дашборд</h1>
          <button
            onClick={() => navigate('/vacancies/create')}
            className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-lg font-medium"
          >
            + Создать вакансию
          </button>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
            {error}
          </div>
        )}

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
                      <p className="text-gray-600 text-sm mb-3 line-clamp-3">
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
