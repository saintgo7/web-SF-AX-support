'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { useAuthApi } from '@/hooks';
import { Button, Input, Select, Alert, Card } from '@/components/ui';
import { RegisterRequest, UserRole } from '@/types';

export default function RegisterPage() {
  const router = useRouter();
  const { register: registerUser } = useAuthApi();
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<RegisterRequest & { confirmPassword: string }>();

  const password = watch('password');

  const onSubmit = async (data: RegisterRequest & { confirmPassword: string }) => {
    try {
      setError(null);
      const { confirmPassword, ...registerData } = data;
      await registerUser.mutateAsync(registerData);
      // Redirect to login page with success message
      router.push('/auth/login?registered=true');
    } catch (err: any) {
      setError(err.response?.data?.detail || '회원가입에 실패했습니다.');
    }
  };

  const roleOptions = [
    { value: 'APPLICANT', label: '신청자' },
    { value: 'EVALUATOR', label: '평가위원' },
  ];

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <Card variant="elevated" className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            회원가입
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            AX 코칭단 평가 시스템에 가입하세요
          </p>
        </div>

        {error && (
          <Alert type="error" onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        <form className="mt-8 space-y-6" onSubmit={handleSubmit(onSubmit)}>
          <div className="space-y-4">
            <Input
              label="이름"
              type="text"
              autoComplete="name"
              placeholder="홍길동"
              error={errors.name?.message}
              {...register('name', {
                required: '이름을 입력해주세요',
                minLength: {
                  value: 2,
                  message: '이름은 최소 2자 이상이어야 합니다',
                },
              })}
            />

            <Input
              label="이메일"
              type="email"
              autoComplete="email"
              placeholder="user@example.com"
              error={errors.email?.message}
              {...register('email', {
                required: '이메일을 입력해주세요',
                pattern: {
                  value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                  message: '올바른 이메일 형식을 입력해주세요',
                },
              })}
            />

            <Input
              label="전화번호 (선택)"
              type="tel"
              autoComplete="tel"
              placeholder="010-1234-5678"
              error={errors.phone?.message}
              {...register('phone', {
                pattern: {
                  value: /^01[0-9]-?\d{3,4}-?\d{4}$/,
                  message: '올바른 전화번호 형식을 입력해주세요',
                },
              })}
            />

            <Select
              label="사용자 유형"
              options={roleOptions}
              placeholder="사용자 유형을 선택하세요"
              error={errors.role?.message}
              {...register('role', {
                required: '사용자 유형을 선택해주세요',
              })}
            />

            <Input
              label="비밀번호"
              type="password"
              autoComplete="new-password"
              placeholder="••••••••"
              error={errors.password?.message}
              {...register('password', {
                required: '비밀번호를 입력해주세요',
                minLength: {
                  value: 8,
                  message: '비밀번호는 최소 8자 이상이어야 합니다',
                },
                pattern: {
                  value: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
                  message: '비밀번호는 영문 대소문자, 숫자를 모두 포함해야 합니다',
                },
              })}
            />

            <Input
              label="비밀번호 확인"
              type="password"
              autoComplete="new-password"
              placeholder="••••••••"
              error={errors.confirmPassword?.message}
              {...register('confirmPassword', {
                required: '비밀번호 확인을 입력해주세요',
                validate: (value) =>
                  value === password || '비밀번호가 일치하지 않습니다',
              })}
            />
          </div>

          <Button
            type="submit"
            fullWidth
            isLoading={isSubmitting}
            disabled={registerUser.isPending}
          >
            가입하기
          </Button>

          <div className="text-center">
            <span className="text-sm text-gray-600">
              이미 계정이 있으신가요?{' '}
              <button
                type="button"
                onClick={() => router.push('/auth/login')}
                className="font-medium text-blue-600 hover:text-blue-500"
              >
                로그인
              </button>
            </span>
          </div>
        </form>
      </Card>
    </div>
  );
}
