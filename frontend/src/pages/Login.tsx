import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import SocialLoginButtons from '../components/SocialLoginButtons';

const Login: React.FC = () => {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [error, setError] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(formData);
      navigate('/');
    } catch (err: any) {
      setError(
        err.response?.data?.non_field_errors?.[0] ||
        err.response?.data?.detail ||
        '로그인에 실패했습니다.'
      );
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
          <h2 className="text-3xl font-black mb-2">로그인</h2>
          <p className="text-base text-muted">AI 창작의 세계에 오신 것을 환영합니다</p>
        </div>

        {error && (
          <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded-xl">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="bg-surface-light dark:bg-surface-dark rounded-xl p-8">
          <div className="mb-6">
            <label htmlFor="email" className="block text-sm font-medium mb-2">
              이메일
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
          </div>

          <div className="mb-6">
            <label htmlFor="password" className="block text-sm font-medium mb-2">
              비밀번호
            </label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="비밀번호를 입력하세요"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-primary text-background-dark font-bold py-3 px-6 rounded-full hover:opacity-90 transition-opacity disabled:opacity-50 mb-4"
          >
            {loading ? '로그인 중...' : '로그인'}
          </button>

          <p className="text-center text-sm mb-6">
            계정이 없으신가요?{' '}
            <Link to="/register" className="text-primary font-semibold hover:underline">
              회원가입
            </Link>
          </p>

          <SocialLoginButtons />
        </form>
      </div>
    </div>
  );
};

export default Login;
