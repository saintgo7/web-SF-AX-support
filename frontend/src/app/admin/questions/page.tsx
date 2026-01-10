'use client';

import { useState, useEffect, useCallback } from 'react';
import { Card, Button, Table, Modal, Input, Textarea, Select } from '@/components/ui';
import { Column } from '@/components/ui/Table';
import { Question, QuestionCategory, QuestionType, Difficulty, Specialty } from '@/types';
import { questionsApi, QuestionCreate, QuestionUpdate } from '@/lib/api/questions';

const QUESTION_TYPES: { value: QuestionType; label: string }[] = [
  { value: 'SINGLE', label: '단일 선택' },
  { value: 'MULTIPLE', label: '다중 선택' },
  { value: 'SHORT', label: '단답형' },
  { value: 'LONG', label: '서술형' },
];

const DIFFICULTY_OPTIONS: { value: Difficulty; label: string }[] = [
  { value: 'EASY', label: '쉬움' },
  { value: 'MEDIUM', label: '보통' },
  { value: 'HARD', label: '어려움' },
];

const SPECIALTY_OPTIONS: { value: Specialty; label: string }[] = [
  { value: 'SMART_FACTORY', label: '스마트팩토리' },
  { value: 'PRODUCTION_MANAGEMENT', label: '생산관리' },
  { value: 'QUALITY_MANAGEMENT', label: '품질관리' },
  { value: 'SAFETY_MANAGEMENT', label: '안전관리' },
  { value: 'ENERGY_MANAGEMENT', label: '에너지관리' },
  { value: 'LOGISTICS', label: '물류' },
  { value: 'MAINTENANCE', label: '설비보전' },
  { value: 'OTHER', label: '기타' },
];

interface FormData {
  category_id: string;
  q_type: QuestionType;
  content: string;
  max_score: number;
  difficulty: Difficulty;
  display_order: number;
  explanation: string;
}

export default function QuestionsPage() {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [categories, setCategories] = useState<QuestionCategory[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedQuestion, setSelectedQuestion] = useState<Question | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  // Form state
  const [formData, setFormData] = useState<FormData>({
    category_id: '',
    q_type: 'LONG',
    content: '',
    max_score: 20,
    difficulty: 'MEDIUM',
    display_order: 0,
    explanation: '',
  });

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const [questionsRes, categoriesRes] = await Promise.all([
        questionsApi.getQuestions({ active_only: false }),
        questionsApi.getCategories(false),
      ]);

      setQuestions(questionsRes.items);
      setCategories(categoriesRes);
    } catch (err) {
      console.error('Failed to fetch data:', err);
      setError('데이터를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const getCategoryName = (categoryId: string): string => {
    const category = categories.find(c => c.id === categoryId);
    return category?.name || '-';
  };

  const getQuestionTypeLabel = (type: QuestionType): string => {
    return QUESTION_TYPES.find(t => t.value === type)?.label || type;
  };

  const getDifficultyLabel = (difficulty: Difficulty): string => {
    return DIFFICULTY_OPTIONS.find(d => d.value === difficulty)?.label || difficulty;
  };

  const columns: Column<Question>[] = [
    {
      key: 'display_order',
      header: '순서',
      render: (_, row) => `#${row.display_order}`,
    },
    {
      key: 'category_id',
      header: '카테고리',
      render: (value) => getCategoryName(value as string),
    },
    {
      key: 'q_type',
      header: '유형',
      render: (value) => (
        <span className="px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800">
          {getQuestionTypeLabel(value as QuestionType)}
        </span>
      ),
    },
    {
      key: 'content',
      header: '문항 내용',
      render: (value) => (
        <span className="text-sm line-clamp-2">{value as string}</span>
      ),
    },
    {
      key: 'difficulty',
      header: '난이도',
      render: (value) => getDifficultyLabel(value as Difficulty),
    },
    {
      key: 'max_score',
      header: '배점',
      render: (value) => `${value}점`,
    },
    {
      key: 'is_active',
      header: '상태',
      render: (value) => (
        <span className={`px-2 py-1 text-xs rounded-full ${
          value ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'
        }`}>
          {value ? '활성' : '비활성'}
        </span>
      ),
    },
    {
      key: 'actions',
      header: '관리',
      render: (_, row) => (
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleEditQuestion(row)}
          >
            수정
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleDeleteQuestion(row.id)}
          >
            삭제
          </Button>
        </div>
      ),
    },
  ];

  const resetForm = () => {
    setFormData({
      category_id: categories[0]?.id || '',
      q_type: 'LONG',
      content: '',
      max_score: 20,
      difficulty: 'MEDIUM',
      display_order: questions.length + 1,
      explanation: '',
    });
  };

  const handleAddQuestion = () => {
    setSelectedQuestion(null);
    resetForm();
    setIsModalOpen(true);
  };

  const handleEditQuestion = (question: Question) => {
    setSelectedQuestion(question);
    setFormData({
      category_id: question.category_id,
      q_type: question.q_type,
      content: question.content,
      max_score: question.max_score,
      difficulty: question.difficulty,
      display_order: question.display_order,
      explanation: question.explanation || '',
    });
    setIsModalOpen(true);
  };

  const handleDeleteQuestion = async (id: string) => {
    if (!confirm('정말 삭제하시겠습니까?')) return;

    try {
      await questionsApi.deleteQuestion(id);
      await fetchData();
    } catch (err) {
      console.error('Failed to delete question:', err);
      alert('삭제에 실패했습니다.');
    }
  };

  const handleSaveQuestion = async () => {
    if (!formData.category_id || !formData.content.trim()) {
      alert('카테고리와 문항 내용을 입력해주세요.');
      return;
    }

    try {
      setIsSaving(true);

      const questionData: QuestionCreate | QuestionUpdate = {
        category_id: formData.category_id,
        q_type: formData.q_type,
        content: formData.content,
        max_score: formData.max_score,
        difficulty: formData.difficulty,
        display_order: formData.display_order,
        explanation: formData.explanation || undefined,
      };

      if (selectedQuestion) {
        await questionsApi.updateQuestion(selectedQuestion.id, questionData);
      } else {
        await questionsApi.createQuestion(questionData as QuestionCreate);
      }

      setIsModalOpen(false);
      setSelectedQuestion(null);
      await fetchData();
    } catch (err) {
      console.error('Failed to save question:', err);
      alert('저장에 실패했습니다.');
    } finally {
      setIsSaving(false);
    }
  };

  const categoryOptions = categories.map(c => ({
    value: c.id,
    label: c.name,
  }));

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-64 gap-4">
        <p className="text-red-600">{error}</p>
        <Button onClick={fetchData}>다시 시도</Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">문항 관리</h1>
          <p className="mt-2 text-gray-600">
            평가 문항을 관리하세요
          </p>
        </div>

        <Button onClick={handleAddQuestion}>
          문항 추가
        </Button>
      </div>

      {/* Questions List */}
      <Card>
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900">
              문항 목록
            </h2>
            <span className="text-sm text-gray-600">
              총 {questions.length}개
            </span>
          </div>

          <Table
            columns={columns}
            data={questions}
            keyField="id"
            emptyMessage="등록된 문항이 없습니다."
          />
        </div>
      </Card>

      {/* Question Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setSelectedQuestion(null);
        }}
        title={selectedQuestion ? '문항 수정' : '새 문항 추가'}
        size="lg"
        footer={
          <>
            <Button
              variant="outline"
              onClick={() => setIsModalOpen(false)}
              disabled={isSaving}
            >
              취소
            </Button>
            <Button onClick={handleSaveQuestion} disabled={isSaving}>
              {isSaving ? '저장 중...' : selectedQuestion ? '수정' : '추가'}
            </Button>
          </>
        }
      >
        <div className="space-y-6">
          <div className="grid grid-cols-2 gap-4">
            <Input
              label="순서"
              type="number"
              placeholder="1"
              value={formData.display_order}
              onChange={(e) => setFormData({ ...formData, display_order: parseInt(e.target.value) || 0 })}
            />

            <Input
              label="배점"
              type="number"
              placeholder="20"
              value={formData.max_score}
              onChange={(e) => setFormData({ ...formData, max_score: parseInt(e.target.value) || 0 })}
            />
          </div>

          <Select
            label="카테고리"
            options={categoryOptions}
            placeholder="카테고리를 선택하세요"
            value={formData.category_id}
            onChange={(e) => setFormData({ ...formData, category_id: e.target.value })}
          />

          <div className="grid grid-cols-2 gap-4">
            <Select
              label="문항 유형"
              options={QUESTION_TYPES}
              value={formData.q_type}
              onChange={(e) => setFormData({ ...formData, q_type: e.target.value as QuestionType })}
            />

            <Select
              label="난이도"
              options={DIFFICULTY_OPTIONS}
              value={formData.difficulty}
              onChange={(e) => setFormData({ ...formData, difficulty: e.target.value as Difficulty })}
            />
          </div>

          <Textarea
            label="문항 내용"
            placeholder="문항 내용을 입력하세요"
            rows={4}
            value={formData.content}
            onChange={(e) => setFormData({ ...formData, content: e.target.value })}
          />

          <Textarea
            label="해설 (선택)"
            placeholder="채점 기준이나 해설을 입력하세요"
            rows={3}
            value={formData.explanation}
            onChange={(e) => setFormData({ ...formData, explanation: e.target.value })}
          />
        </div>
      </Modal>
    </div>
  );
}
