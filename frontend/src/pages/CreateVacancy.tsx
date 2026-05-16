import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import { vacanciesApi } from '../api/vacancies';
import { specializationsApi } from '../api/specializations';
import { Specialization } from '../types';

const CreateVacancy: React.FC = () => {
  const navigate = useNavigate();
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [specializationId, setSpecializationId] = useState<number | ''>('');
  const [specializations, setSpecializations] = useState<Specialization[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadSpecializations();
  }, []);

  const loadSpecializations = async () => {
    try {
      const data = await specializationsApi.getAll();
      setSpecializations(data);
    } catch (err: any) {
      setError('Ошибка загрузки специализаций: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!title.trim() || !description.trim() || !specializationId) {
      setError('Заполните все обязательные поля');
      return;
    }

    setLoading(true);
    try {
      await vacanciesApi.create({
        title: title.trim(),
        description: description.trim(),
        specialization_id: Number(specializationId),
        is_active: true,
      });
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка создания вакансии');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <div className="max-w-2xl mx-auto px-4 sm:px-0">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Создать вакансию</h1>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
            {error}
          </div>
        )}

        <div className="bg-white shadow-md rounded-lg p-6">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-2">
                Название вакансии <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                id="title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Например: Senior Python Developer"
                required
                minLength={5}
                maxLength={255}
              />
            </div>

            <div>
              <label htmlFor="specialization" className="block text-sm font-medium text-gray-700 mb-2">
                Специализация <span className="text-red-500">*</span>
              </label>
              <select
                id="specialization"
                value={specializationId}
                onChange={(e) => setSpecializationId(Number(e.target.value))}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              >
                <option value="">Выберите специализацию</option>
                {specializations.map((spec) => (
                  <option key={spec.specialization_id} value={spec.specialization_id}>
                    {spec.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
                Описание требований <span className="text-red-500">*</span>
              </label>
              <textarea
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={10}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Опишите требования к кандидату, необходимые навыки, опыт работы..."
                required
              />
            </div>

            <div className="flex gap-4">
              <button
                type="submit"
                disabled={loading}
                className="flex-1 bg-blue-500 hover:bg-blue-600 text-white font-medium py-3 px-6 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Создание...' : 'Создать вакансию'}
              </button>
              <button
                type="button"
                onClick={() => navigate('/dashboard')}
                className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-700 font-medium py-3 px-6 rounded-lg"
              >
                Отмена
              </button>
            </div>
          </form>
        </div>
      </div>
    </Layout>
  );
};

export default CreateVacancy;
