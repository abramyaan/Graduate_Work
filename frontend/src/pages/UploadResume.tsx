import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import Layout from '../components/Layout';
import { useToast } from '../context/ToastContext';
import { candidatesApi } from '../api/candidates';
import { resumesApi } from '../api/resumes';
import { vacanciesApi } from '../api/vacancies';
import { Vacancy } from '../types';

const UploadResume: React.FC = () => {
  const navigate = useNavigate();
  const { showSuccess, showError } = useToast();
  const { vacancyId } = useParams<{ vacancyId?: string }>();

  const [lastName, setLastName] = useState('');
  const [firstName, setFirstName] = useState('');
  const [patronymic, setPatronymic] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [selectedVacancyId, setSelectedVacancyId] = useState<number | ''>(vacancyId ? Number(vacancyId) : '');
  const [file, setFile] = useState<File | null>(null);

  const [vacancies, setVacancies] = useState<Vacancy[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadVacancies();
  }, []);

  const loadVacancies = async () => {
    try {
      const data = await vacanciesApi.getActive();
      setVacancies(data);
    } catch (err: any) {
      setError('Ошибка загрузки вакансий: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      const ext = selectedFile.name.split('.').pop()?.toLowerCase();

      if (ext !== 'pdf' && ext !== 'docx') {
        setError('Разрешены только файлы PDF и DOCX');
        setFile(null);
        return;
      }

      setFile(selectedFile);
      setError('');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!lastName.trim() || !firstName.trim()) {
      setError('Введите фамилию и имя кандидата');
      return;
    }

    if (!file) {
      setError('Выберите файл резюме');
      return;
    }

    if (!selectedVacancyId) {
      setError('Выберите вакансию');
      return;
    }

    setLoading(true);
    try {
      // Создаем кандидата
      const candidate = await candidatesApi.create({
        last_name: lastName.trim(),
        first_name: firstName.trim(),
        patronymic: patronymic.trim() || undefined,
        email: email.trim() || undefined,
        phone: phone.trim() || undefined,
      });

      // Загружаем резюме
      await resumesApi.upload(file, candidate.candidate_id, Number(selectedVacancyId));

      // Перенаправляем на дашборд
      showSuccess('Резюме успешно загружено!');
      navigate('/dashboard');
    } catch (err: any) {
      setError(
        typeof err.response?.data === 'string'
          ? err.response.data
          : err.response?.data?.detail || err.response?.data?.error || 'Ошибка загрузки резюме'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <div className="max-w-2xl mx-auto px-4 sm:px-0">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Загрузить резюме</h1>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
            {error}
          </div>
        )}

        <div className="bg-white shadow-md rounded-lg p-6">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="lastName" className="block text-sm font-medium text-gray-700 mb-2">
                  Фамилия <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  id="lastName"
                  value={lastName}
                  onChange={(e) => setLastName(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Иванов"
                  required
                  maxLength={100}
                />
              </div>

              <div>
                <label htmlFor="firstName" className="block text-sm font-medium text-gray-700 mb-2">
                  Имя <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  id="firstName"
                  value={firstName}
                  onChange={(e) => setFirstName(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Иван"
                  required
                  maxLength={100}
                />
              </div>
            </div>

            <div>
              <label htmlFor="patronymic" className="block text-sm font-medium text-gray-700 mb-2">
                Отчество
              </label>
              <input
                type="text"
                id="patronymic"
                value={patronymic}
                onChange={(e) => setPatronymic(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Иванович"
                maxLength={100}
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                  Email
                </label>
                <input
                  type="email"
                  id="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="ivanov@example.com"
                  maxLength={255}
                />
              </div>

              <div>
                <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-2">
                  Телефон
                </label>
                <input
                  type="tel"
                  id="phone"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="+7 (999) 123-45-67"
                  maxLength={20}
                />
              </div>
            </div>

            <div>
              <label htmlFor="vacancy" className="block text-sm font-medium text-gray-700 mb-2">
                Вакансия <span className="text-red-500">*</span>
              </label>
              <select
                id="vacancy"
                value={selectedVacancyId}
                onChange={(e) => setSelectedVacancyId(Number(e.target.value))}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              >
                <option value="">Выберите вакансию</option>
                {vacancies.map((vacancy) => (
                  <option key={vacancy.vacancy_id} value={vacancy.vacancy_id}>
                    {vacancy.title}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label htmlFor="file" className="block text-sm font-medium text-gray-700 mb-2">
                Файл резюме (PDF или DOCX) <span className="text-red-500">*</span>
              </label>
              <input
                type="file"
                id="file"
                accept=".pdf,.docx"
                onChange={handleFileChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                required
              />
              {file && (
                <p className="mt-2 text-sm text-gray-600">
                  Выбран файл: <span className="font-medium">{file.name}</span> ({(file.size / 1024).toFixed(1)} KB)
                </p>
              )}
            </div>

            <div className="flex gap-4">
              <button
                type="submit"
                disabled={loading}
                className="flex-1 bg-blue-500 hover:bg-blue-600 text-white font-medium py-3 px-6 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Загрузка...' : 'Загрузить резюме'}
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

export default UploadResume;
