import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Register: React.FC = () => {
  const navigate = useNavigate();
  const { register } = useAuth();

  const [formData, setFormData] = useState({
    email: '',
    nickname: '',
    password: '',
    password_confirm: '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState<boolean>(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    // 해당 필드의 에러 제거
    if (errors[e.target.name]) {
      setErrors({
        ...errors,
        [e.target.name]: '',
      });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});
    setLoading(true);

    // 클라이언트 측 검증
    if (formData.password !== formData.password_confirm) {
      setErrors({ password_confirm: '비밀번호가 일치하지 않습니다.' });
      setLoading(false);
      return;
    }

    try {
      await register(formData);
      navigate('/');
    } catch (err: any) {
      const responseErrors = err.response?.data;
      if (typeof responseErrors === 'object') {
        setErrors(responseErrors);
      } else {
        setErrors({ general: '회원가입에 실패했습니다.' });
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background-light dark:bg-background-dark flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center gap-3 text-text-light dark:text-text-dark mb-4">
            <div className="size-8 text-primary">
              <svg fill="none" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
                <path
                  clipRule="evenodd"
                  d="M12.0799 24L4 19.2479L9.95537 8.75216L18.04 13.4961L18.0446 4H29.9554L29.96 13.4961L38.0446 8.75216L44 19.2479L35.92 24L44 28.7521L38.0446 39.2479L29.96 34.5039L29.9554 44H18.0446L18.04 34.5039L9.95537 39.2479L4 28.7521L12.0799 24Z"
                  fill="currentColor"
                  fillRule="evenodd"
                ></path>
              </svg>
            </div>
            <h1 className="text-2xl font-bold">Artlion</h1>
          </Link>
          <h2 className="text-3xl font-black mb-2">회원가입</h2>
          <p className="text-base text-muted">새로운 계정을 만들어보세요</p>
        </div>

        {errors.general && (
          <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded-xl">
            {errors.general}
          </div>
        )}

        <form onSubmit={handleSubmit} className="bg-surface-light dark:bg-surface-dark rounded-xl p-8">
          <div className="mb-6">
            <label htmlFor="email" className="block text-sm font-medium mb-2">
              이메일 *
            </label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="example@email.com"
            />
            {errors.email && <p className="mt-1 text-sm text-red-600">{errors.email}</p>}
          </div>

          <div className="mb-6">
            <label htmlFor="nickname" className="block text-sm font-medium mb-2">
              닉네임 *
            </label>
            <input
              type="text"
              id="nickname"
              name="nickname"
              value={formData.nickname}
              onChange={handleChange}
              required
              minLength={2}
              maxLength={50}
              className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="사용할 닉네임을 입력하세요"
            />
            {errors.nickname && <p className="mt-1 text-sm text-red-600">{errors.nickname}</p>}
            <small className="text-xs text-gray-500 mt-1 block">2-50자 이내로 입력해주세요</small>
          </div>

          <div className="mb-6">
            <label htmlFor="password" className="block text-sm font-medium mb-2">
              비밀번호 *
            </label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              minLength={8}
              className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="8자 이상의 비밀번호"
            />
            {errors.password && <p className="mt-1 text-sm text-red-600">{errors.password}</p>}
            <small className="text-xs text-gray-500 mt-1 block">
              최소 8자 이상, 영문/숫자/특수문자 포함 권장
            </small>
          </div>

          <div className="mb-6">
            <label htmlFor="password_confirm" className="block text-sm font-medium mb-2">
              비밀번호 확인 *
            </label>
            <input
              type="password"
              id="password_confirm"
              name="password_confirm"
              value={formData.password_confirm}
              onChange={handleChange}
              required
              minLength={8}
              className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="비밀번호를 다시 입력하세요"
            />
            {errors.password_confirm && (
              <p className="mt-1 text-sm text-red-600">{errors.password_confirm}</p>
            )}
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-primary text-background-dark font-bold py-3 px-6 rounded-full hover:opacity-90 transition-opacity disabled:opacity-50 mb-4"
          >
            {loading ? '가입 중...' : '회원가입'}
          </button>

          <p className="text-center text-sm">
            이미 계정이 있으신가요?{' '}
            <Link to="/login" className="text-primary font-semibold hover:underline">
              로그인
            </Link>
          </p>
        </form>
      </div>
    </div>
  );
};

export default Register;
