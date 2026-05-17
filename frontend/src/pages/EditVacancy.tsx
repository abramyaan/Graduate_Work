import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import LoadingSpinner from '../components/LoadingSpinner';
import ConfirmDialog from '../components/ConfirmDialog';
import { useToast } from '../context/ToastContext';
import { vacanciesApi } from '../api/vacancies';
import { specializationsApi } from '../api/specializations';
import { Vacancy, Specialization } from '../types';

const EditVacancy: React.FC = () => {
  const { vacancyId } = useParams<{ vacancyId: string }>();
  const navigate = useNavigate();
  const { showSuccess, showError } = useToast();

  const [, setVacancy] = useState<Vacancy | null>(null);
  const [specializations, setSpecializations] = useState<Specialization[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);

  const [formData, setFormData] = useState({
    title: '',
    description: '',
    specialization_id: 0,
    is_active: true,
  });

  const [errors, setErrors] = useState({
    title: '',
    description: '',
    specialization_id: '',
  });

  useEffect(() => {
    loadData();
  }, [vacancyId]);

  const loadData = async () => {
    try {
      const [vacancyData, specializationsData] = await Promise.all([
        vacanciesApi.getById(Number(vacancyId)),
        specializationsApi.getAll(),
      ]);

      setVacancy(vacancyData);
      setSpecializations(specializationsData);
      setFormData({
        title: vacancyData.title,
        description: vacancyData.description,
        specialization_id: vacancyData.specialization_id,
        is_active: vacancyData.is_active,
      });
    } catch (err: any) {
      showError('Ошибка загрузки данных: ' + (err.response?.data?.detail || err.message));
      navigate('/dashboard');
    } finally {
      setLoading(false);
    }
  };

  const validateForm = (): boolean => {
    const newErrors = {
      title: '',
      description: '',
      specialization_id: '',
    };

    if (!formData.title.trim()) {
      newErrors.title = 'Название вакансии обязательно';
    } else if (formData.title.trim().length < 5) {
      newErrors.title = 'Название должно содержать минимум 5 символов';
    }

    if (!formData.description.trim()) {
      newErrors.description = 'Описание вакансии обязательно';
    } else if (formData.description.trim().length < 20) {
      newErrors.description = 'Описание должно содержать минимум 20 символов';
    }

    if (!formData.specialization_id || formData.specialization_id === 0) {
      newErrors.specialization_id = 'Выберите специализацию';
    }

    setErrors(newErrors);
    return !Object.values(newErrors).some((error) => error !== '');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      showError('Пожалуйста, исправьте ошибки в форме');
      return;
    }

    setSubmitting(true);
    try {
      await vacanciesApi.update(Number(vacancyId), formData);
      showSuccess('Вакансия успешно обновлена!');
      navigate('/dashboard');
    } catch (err: any) {
      showError('Ошибка обновления: ' + (err.response?.data?.detail || err.message));
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async () => {
    try {
      await vacanciesApi.delete(Number(vacancyId));
      showSuccess('Вакансия успешно удалена');
      navigate('/dashboard');
    } catch (err: any) {
      showError('Ошибка удаления: ' + (err.response?.data?.detail || err.message));
      setShowDeleteDialog(false);
    }
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
      <div className="max-w-3xl mx-auto px-4 sm:px-0">
        <div className="mb-6">
          <button
            onClick={() => navigate('/dashboard')}
            className="text-blue-600 hover:text-blue-800 mb-4 flex items-center"
          >
            ← Назад к дашборду
          </button>
          <h1 className="text-3xl font-bold text-gray-900">Редактировать вакансию</h1>
        </div>

        <form onSubmit={handleSubmit} className="bg-white shadow-md rounded-lg p-6">
          {/* Название */}
          <div className="mb-6">
            <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-2">
              Название вакансии *
            </label>
            <input
              type="text"
              id="title"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                errors.title ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="Например: Frontend Developer"
            />
            {errors.title && <p className="mt-1 text-sm text-red-600">{errors.title}</p>}
          </div>

          {/* Специализация */}
          <div className="mb-6">
            <label
              htmlFor="specialization"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Специализация *
            </label>
            <select
              id="specialization"
              value={formData.specialization_id}
              onChange={(e) =>
                setFormData({ ...formData, specialization_id: Number(e.target.value) })
              }
              className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                errors.specialization_id ? 'border-red-500' : 'border-gray-300'
              }`}
            >
              <option value={0}>Выберите специализацию</option>
              {specializations.map((spec) => (
                <option key={spec.specialization_id} value={spec.specialization_id}>
                  {spec.name}
                </option>
              ))}
            </select>
            {errors.specialization_id && (
              <p className="mt-1 text-sm text-red-600">{errors.specialization_id}</p>
            )}
          </div>

          {/* Описание */}
          <div className="mb-6">
            <label
              htmlFor="description"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Описание вакансии *
            </label>
            <textarea
              id="description"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              rows={10}
              className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                errors.description ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="Подробное описание вакансии, требования к кандидату, обязанности..."
            />
            {errors.description && (
              <p className="mt-1 text-sm text-red-600">{errors.description}</p>
            )}
          </div>

          {/* Статус */}
          <div className="mb-6">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={formData.is_active}
                onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <span className="ml-2 text-sm text-gray-700">Вакансия активна</span>
            </label>
          </div>

          {/* Кнопки */}
          <div className="flex justify-between items-center">
            <button
              type="button"
              onClick={() => setShowDeleteDialog(true)}
              className="bg-red-500 hover:bg-red-600 text-white px-6 py-2 rounded-lg font-medium"
            >
              Удалить вакансию
            </button>

            <div className="flex space-x-3">
              <button
                type="button"
                onClick={() => navigate('/dashboard')}
                className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 font-medium"
              >
                Отмена
              </button>
              <button
                type="submit"
                disabled={submitting}
                className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-lg font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {submitting ? 'Сохранение...' : 'Сохранить изменения'}
              </button>
            </div>
          </div>
        </form>

        {/* Диалог подтверждения удаления */}
        <ConfirmDialog
          isOpen={showDeleteDialog}
          title="Удалить вакансию?"
          message="Вы уверены, что хотите удалить эту вакансию? Это действие нельзя отменить. Все связанные резюме и оценки также будут удалены."
          confirmText="Да, удалить"
          cancelText="Отмена"
          type="danger"
          onConfirm={handleDelete}
          onCancel={() => setShowDeleteDialog(false)}
        />
      </div>
    </Layout>
  );
};

export default EditVacancy;
