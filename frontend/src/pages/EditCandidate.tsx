import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import LoadingSpinner from '../components/LoadingSpinner';
import { useToast } from '../context/ToastContext';
import { candidatesApi } from '../api/candidates';
import { Candidate } from '../types';

const EditCandidate: React.FC = () => {
  const { candidateId } = useParams<{ candidateId: string }>();
  const navigate = useNavigate();
  const { showSuccess, showError } = useToast();

  const [candidate, setCandidate] = useState<Candidate | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  const [formData, setFormData] = useState({
    last_name: '',
    first_name: '',
    patronymic: '',
    email: '',
    phone: '',
  });

  const [errors, setErrors] = useState({
    last_name: '',
    first_name: '',
    email: '',
    phone: '',
  });

  useEffect(() => {
    loadCandidate();
  }, [candidateId]);

  const loadCandidate = async () => {
    try {
      const data = await candidatesApi.getById(Number(candidateId));
      setCandidate(data);
      setFormData({
        last_name: data.last_name,
        first_name: data.first_name,
        patronymic: data.patronymic || '',
        email: data.email || '',
        phone: data.phone || '',
      });
    } catch (err: any) {
      showError('Ошибка загрузки данных: ' + (err.response?.data?.detail || err.message));
      navigate('/candidates');
    } finally {
      setLoading(false);
    }
  };

  const validateForm = (): boolean => {
    const newErrors = {
      last_name: '',
      first_name: '',
      email: '',
      phone: '',
    };

    if (!formData.last_name.trim()) {
      newErrors.last_name = 'Фамилия обязательна';
    } else if (formData.last_name.trim().length < 2) {
      newErrors.last_name = 'Фамилия должна содержать минимум 2 символа';
    }

    if (!formData.first_name.trim()) {
      newErrors.first_name = 'Имя обязательно';
    } else if (formData.first_name.trim().length < 2) {
      newErrors.first_name = 'Имя должно содержать минимум 2 символа';
    }

    if (formData.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Некорректный email';
    }

    if (formData.phone && !/^[+]?[0-9\s\-()]{7,20}$/.test(formData.phone)) {
      newErrors.phone = 'Некорректный номер телефона';
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
      // Убираем пустые поля
      const updateData: any = {
        last_name: formData.last_name,
        first_name: formData.first_name,
      };

      if (formData.patronymic) updateData.patronymic = formData.patronymic;
      if (formData.email) updateData.email = formData.email;
      if (formData.phone) updateData.phone = formData.phone;

      await candidatesApi.update(Number(candidateId), updateData);
      showSuccess('Кандидат успешно обновлен!');
      navigate('/candidates');
    } catch (err: any) {
      showError('Ошибка обновления: ' + (err.response?.data?.detail || err.message));
    } finally {
      setSubmitting(false);
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
      <div className="max-w-2xl mx-auto px-4 sm:px-0">
        <div className="mb-6">
          <button
            onClick={() => navigate('/candidates')}
            className="text-blue-600 hover:text-blue-800 mb-4 flex items-center"
          >
            ← Назад к списку кандидатов
          </button>
          <h1 className="text-3xl font-bold text-gray-900">Редактировать кандидата</h1>
        </div>

        <form onSubmit={handleSubmit} className="bg-white shadow-md rounded-lg p-6">
          {/* Фамилия */}
          <div className="mb-6">
            <label htmlFor="last_name" className="block text-sm font-medium text-gray-700 mb-2">
              Фамилия *
            </label>
            <input
              type="text"
              id="last_name"
              value={formData.last_name}
              onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
              className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                errors.last_name ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="Иванов"
            />
            {errors.last_name && <p className="mt-1 text-sm text-red-600">{errors.last_name}</p>}
          </div>

          {/* Имя */}
          <div className="mb-6">
            <label htmlFor="first_name" className="block text-sm font-medium text-gray-700 mb-2">
              Имя *
            </label>
            <input
              type="text"
              id="first_name"
              value={formData.first_name}
              onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
              className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                errors.first_name ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="Иван"
            />
            {errors.first_name && <p className="mt-1 text-sm text-red-600">{errors.first_name}</p>}
          </div>

          {/* Отчество */}
          <div className="mb-6">
            <label htmlFor="patronymic" className="block text-sm font-medium text-gray-700 mb-2">
              Отчество
            </label>
            <input
              type="text"
              id="patronymic"
              value={formData.patronymic}
              onChange={(e) => setFormData({ ...formData, patronymic: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Иванович"
            />
          </div>

          {/* Email */}
          <div className="mb-6">
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
              Email
            </label>
            <input
              type="email"
              id="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                errors.email ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="ivan@example.com"
            />
            {errors.email && <p className="mt-1 text-sm text-red-600">{errors.email}</p>}
          </div>

          {/* Телефон */}
          <div className="mb-6">
            <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-2">
              Телефон
            </label>
            <input
              type="tel"
              id="phone"
              value={formData.phone}
              onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
              className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                errors.phone ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="+7 900 123-45-67"
            />
            {errors.phone && <p className="mt-1 text-sm text-red-600">{errors.phone}</p>}
          </div>

          {/* Кнопки */}
          <div className="flex justify-end space-x-3">
            <button
              type="button"
              onClick={() => navigate('/candidates')}
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
        </form>
      </div>
    </Layout>
  );
};

export default EditCandidate;
