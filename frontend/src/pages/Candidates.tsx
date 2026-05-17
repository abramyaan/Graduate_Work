import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import LoadingSpinner from '../components/LoadingSpinner';
import ConfirmDialog from '../components/ConfirmDialog';
import { useToast } from '../context/ToastContext';
import { candidatesApi } from '../api/candidates';
import { Candidate } from '../types';

const Candidates: React.FC = () => {
  const navigate = useNavigate();
  const { showSuccess, showError } = useToast();

  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [filteredCandidates, setFilteredCandidates] = useState<Candidate[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [deleteCandidate, setDeleteCandidate] = useState<Candidate | null>(null);

  useEffect(() => {
    loadCandidates();
  }, []);

  useEffect(() => {
    filterCandidates();
  }, [searchQuery, candidates]);

  const loadCandidates = async () => {
    try {
      const data = await candidatesApi.getAll();
      setCandidates(data);
      setFilteredCandidates(data);
    } catch (err: any) {
      showError('Ошибка загрузки кандидатов: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const filterCandidates = () => {
    if (!searchQuery.trim()) {
      setFilteredCandidates(candidates);
      return;
    }

    const query = searchQuery.toLowerCase();
    const filtered = candidates.filter(
      (candidate) =>
        candidate.last_name.toLowerCase().includes(query) ||
        candidate.first_name.toLowerCase().includes(query) ||
        (candidate.patronymic && candidate.patronymic.toLowerCase().includes(query)) ||
        (candidate.email && candidate.email.toLowerCase().includes(query)) ||
        (candidate.phone && candidate.phone.includes(query))
    );

    setFilteredCandidates(filtered);
  };

  const handleDelete = async () => {
    if (!deleteCandidate) return;

    try {
      await candidatesApi.delete(deleteCandidate.candidate_id);
      showSuccess('Кандидат успешно удален');
      setCandidates(candidates.filter((c) => c.candidate_id !== deleteCandidate.candidate_id));
      setDeleteCandidate(null);
    } catch (err: any) {
      showError('Ошибка удаления: ' + (err.response?.data?.detail || err.message));
      setDeleteCandidate(null);
    }
  };

  const getCandidateName = (candidate: Candidate) => {
    let name = `${candidate.last_name} ${candidate.first_name}`;
    if (candidate.patronymic) {
      name += ` ${candidate.patronymic}`;
    }
    return name;
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
          <div className="flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-900">Кандидаты</h1>
          </div>
        </div>

        {/* Поиск */}
        <div className="mb-6">
          <div className="relative">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Поиск по имени, email или телефону..."
              className="w-full px-4 py-3 pl-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <svg
              className="absolute left-3 top-3.5 h-5 w-5 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
          </div>
          <p className="mt-2 text-sm text-gray-600">
            Найдено: {filteredCandidates.length} из {candidates.length}
          </p>
        </div>

        {/* Таблица кандидатов */}
        <div className="bg-white shadow-md rounded-lg overflow-hidden">
          {filteredCandidates.length === 0 ? (
            <div className="px-6 py-8 text-center text-gray-500">
              {searchQuery ? 'Кандидаты не найдены' : 'Нет кандидатов'}
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      ФИО
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Email
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Телефон
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Действия
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {filteredCandidates.map((candidate) => (
                    <tr key={candidate.candidate_id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {getCandidateName(candidate)}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-500">
                          {candidate.email || '—'}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-500">
                          {candidate.phone || '—'}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <button
                          onClick={() => navigate(`/candidates/edit/${candidate.candidate_id}`)}
                          className="text-blue-600 hover:text-blue-900 font-medium mr-4"
                        >
                          Редактировать
                        </button>
                        <button
                          onClick={() => setDeleteCandidate(candidate)}
                          className="text-red-600 hover:text-red-900 font-medium"
                        >
                          Удалить
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Диалог подтверждения удаления */}
        <ConfirmDialog
          isOpen={!!deleteCandidate}
          title="Удалить кандидата?"
          message={`Вы уверены, что хотите удалить ${
            deleteCandidate ? getCandidateName(deleteCandidate) : ''
          }? Это действие нельзя отменить.`}
          confirmText="Да, удалить"
          cancelText="Отмена"
          type="danger"
          onConfirm={handleDelete}
          onCancel={() => setDeleteCandidate(null)}
        />
      </div>
    </Layout>
  );
};

export default Candidates;
