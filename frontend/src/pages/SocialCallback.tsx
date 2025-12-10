import React, { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import authService from '../services/authService';

const SocialCallback: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { user, login } = useAuth();

  useEffect(() => {
    const handleCallback = async () => {
      // URL 파라미터에서 토큰 추출
      const accessToken = searchParams.get('access_token');
      const refreshToken = searchParams.get('refresh_token');
      const error = searchParams.get('error');

      if (error) {
        console.error('Social login error:', error);
        navigate('/login?error=' + error);
        return;
      }

      if (accessToken && refreshToken) {
        try {
          // 토큰 저장
          localStorage.setItem('access_token', accessToken);
          localStorage.setItem('refresh_token', refreshToken);

          // 사용자 정보 가져오기
          const currentUser = await authService.getCurrentUser();
          localStorage.setItem('user', JSON.stringify(currentUser));

          // 대시보드로 리다이렉트
          navigate('/', { replace: true });
        } catch (error) {
          console.error('Failed to get user info:', error);
          navigate('/login?error=user_info_failed');
        }
      } else {
        navigate('/login?error=no_tokens');
      }
    };

    handleCallback();
  }, [searchParams, navigate]);

  return (
    <div className="min-h-screen bg-background-light dark:bg-background-dark flex items-center justify-center">
      <div className="text-center">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
        <p className="mt-4 text-lg">로그인 처리 중...</p>
      </div>
    </div>
  );
};

export default SocialCallback;
