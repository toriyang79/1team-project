import React from 'react';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

interface SocialLoginButtonsProps {
  redirectUri?: string;
}

const SocialLoginButtons: React.FC<SocialLoginButtonsProps> = ({ redirectUri }) => {
  const handleSocialLogin = (provider: 'google' | 'github' | 'naver' | 'kakao') => {
    const currentRedirectUri = redirectUri || window.location.origin;
    const socialLoginUrl = `${API_BASE_URL}/social/${provider}/?redirect_uri=${encodeURIComponent(currentRedirectUri)}`;

    // 새 창이 아닌 현재 페이지에서 리다이렉트
    window.location.href = socialLoginUrl;
  };

  return (
    <div className="space-y-3">
      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-gray-300 dark:border-gray-600"></div>
        </div>
        <div className="relative flex justify-center text-sm">
          <span className="px-2 bg-white dark:bg-background-dark text-gray-500">
            또는 소셜 계정으로 계속하기
          </span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        {/* Google */}
        <button
          onClick={() => handleSocialLogin('google')}
          className="flex items-center justify-center gap-2 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
        >
          <svg className="w-5 h-5" viewBox="0 0 24 24">
            <path
              fill="#4285F4"
              d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
            />
            <path
              fill="#34A853"
              d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
            />
            <path
              fill="#FBBC05"
              d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
            />
            <path
              fill="#EA4335"
              d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
            />
          </svg>
          <span className="text-sm font-medium">Google</span>
        </button>

        {/* GitHub */}
        <button
          onClick={() => handleSocialLogin('github')}
          className="flex items-center justify-center gap-2 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
        >
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
            <path
              fillRule="evenodd"
              d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"
              clipRule="evenodd"
            />
          </svg>
          <span className="text-sm font-medium">GitHub</span>
        </button>

        {/* Naver */}
        <button
          onClick={() => handleSocialLogin('naver')}
          className="flex items-center justify-center gap-2 px-4 py-2 bg-[#03C75A] text-white rounded-lg hover:bg-[#02B350] transition-colors"
        >
          <svg className="w-5 h-5" viewBox="0 0 24 24" fill="white">
            <path d="M16.273 12.845L7.376 0H0v24h7.726V11.156L16.624 24H24V0h-7.727v12.845z" />
          </svg>
          <span className="text-sm font-medium">네이버</span>
        </button>

        {/* Kakao */}
        <button
          onClick={() => handleSocialLogin('kakao')}
          className="flex items-center justify-center gap-2 px-4 py-2 bg-[#FEE500] text-[#000000] rounded-lg hover:bg-[#FDD835] transition-colors"
        >
          <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 3c5.799 0 10.5 3.664 10.5 8.185 0 4.52-4.701 8.184-10.5 8.184a13.5 13.5 0 01-1.727-.11l-4.408 2.883c-.501.265-.678.236-.472-.413l.892-3.678c-2.88-1.46-4.785-3.99-4.785-6.866C1.5 6.665 6.201 3 12 3z" />
          </svg>
          <span className="text-sm font-medium">카카오</span>
        </button>
      </div>
    </div>
  );
};

export default SocialLoginButtons;
