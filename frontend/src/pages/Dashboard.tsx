import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Dashboard: React.FC = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();
  const [theme, setTheme] = useState<'light' | 'dark'>('light');
  const [activeFilter, setActiveFilter] = useState<'all' | 'image' | 'music' | 'video'>('all');

  // 테마 초기화
  useEffect(() => {
    const savedTheme = (localStorage.getItem('theme') as 'light' | 'dark') || 'light';
    setTheme(savedTheme);
    document.documentElement.classList.toggle('dark', savedTheme === 'dark');
  }, []);

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
    document.documentElement.classList.toggle('dark', newTheme === 'dark');
  };

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/login');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  const filterContent = (filter: 'all' | 'image' | 'music' | 'video') => {
    setActiveFilter(filter);
  };

  return (
    <div className="relative flex min-h-screen w-full flex-col bg-background-light dark:bg-background-dark text-text-light dark:text-text-dark">
      <div className="layout-container flex h-full grow flex-col">
        <div className="px-4 sm:px-8 md:px-16 lg:px-24 xl:px-40 flex flex-1 justify-center py-5">
          <div className="layout-content-container flex flex-col w-full max-w-6xl flex-1">
            {/* Navigation Bar */}
            <header className="flex items-center justify-between whitespace-nowrap border-b border-solid border-gray-300 dark:border-gray-700 px-4 py-3">
              <div className="flex items-center gap-8">
                <Link
                  to="/"
                  className="flex items-center gap-3 hover:opacity-80 transition-opacity"
                >
                  <div className="size-6 text-primary">
                    <svg fill="none" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
                      <path
                        clipRule="evenodd"
                        d="M12.0799 24L4 19.2479L9.95537 8.75216L18.04 13.4961L18.0446 4H29.9554L29.96 13.4961L38.0446 8.75216L44 19.2479L35.92 24L44 28.7521L38.0446 39.2479L29.96 34.5039L29.9554 44H18.0446L18.04 34.5039L9.95537 39.2479L4 28.7521L12.0799 24Z"
                        fill="currentColor"
                        fillRule="evenodd"
                      ></path>
                    </svg>
                  </div>
                  <h2 className="text-xl font-bold">Artlion</h2>
                </Link>
                <nav className="hidden md:flex items-center gap-9">
                  <button className="text-sm font-medium hover:text-primary transition-colors">
                    이미지
                  </button>
                  <button className="text-sm font-medium hover:text-primary transition-colors">
                    음악
                  </button>
                  <button className="text-sm font-medium hover:text-primary transition-colors">
                    비디오
                  </button>
                </nav>
              </div>
              <div className="flex flex-1 justify-end items-center gap-4">
                <button
                  onClick={toggleTheme}
                  className="flex items-center justify-center h-10 w-10 rounded-full bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
                  aria-label="Toggle theme"
                >
                  <span className="text-2xl">{theme === 'dark' ? '☀️' : '🌙'}</span>
                </button>
                <div className="flex gap-2">
                  {isAuthenticated && user ? (
                    <>
                      <span className="flex items-center text-sm font-medium px-4">
                        👋 {user.nickname}님
                      </span>
                      <button
                        onClick={handleLogout}
                        className="flex min-w-[84px] cursor-pointer items-center justify-center overflow-hidden rounded-full h-10 px-4 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-sm font-bold transition-colors"
                      >
                        <span>로그아웃</span>
                      </button>
                    </>
                  ) : (
                    <>
                      <Link
                        to="/register"
                        className="flex min-w-[84px] cursor-pointer items-center justify-center overflow-hidden rounded-full h-10 px-4 bg-primary text-background-dark text-sm font-bold hover:opacity-90 transition-opacity"
                      >
                        <span>회원가입</span>
                      </Link>
                      <Link
                        to="/login"
                        className="flex min-w-[84px] cursor-pointer items-center justify-center overflow-hidden rounded-full h-10 px-4 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-sm font-bold transition-colors"
                      >
                        <span>로그인</span>
                      </Link>
                    </>
                  )}
                </div>
              </div>
            </header>

            {/* Hero Section */}
            <div className="@container">
              <div className="@[480px]:p-4">
                <div className="flex min-h-[480px] flex-col gap-6 bg-cover bg-center bg-no-repeat @[480px]:gap-8 @[480px]:rounded-xl items-start justify-end px-4 pb-10 @[480px]:px-10"
                  style={{
                    backgroundImage: 'linear-gradient(rgba(0, 0, 0, 0.1) 0%, rgba(0, 0, 0, 0.4) 100%), url("https://cdn.usegalileo.ai/sdxl10/b5e3e3a8-2c0c-4e3f-9c6e-9b7a5c7b8e4d.png")'
                  }}>
                  <div className="flex flex-col gap-4 text-left">
                    <h1 className="text-4xl font-black leading-tight tracking-[-0.033em] @[480px]:text-5xl @[864px]:text-6xl text-white">
                      Artlion과 함께하는 AI 창작의 세계
                    </h1>
                    <h2 className="text-base font-normal leading-normal @[480px]:text-lg text-white">
                      인공지능이 만든 놀라운 이미지, 음악, 비디오를 발견하고 공유하세요.
                    </h2>
                  </div>
                  {!isAuthenticated && (
                    <Link
                      to="/register"
                      className="flex self-start min-w-[84px] cursor-pointer items-center justify-center overflow-hidden rounded-full h-12 px-6 bg-primary text-background-dark text-base font-bold hover:opacity-90 transition-opacity"
                    >
                      <span>지금 시작하기</span>
                    </Link>
                  )}
                </div>
              </div>
            </div>

            {/* Filter Chips */}
            <div className="flex gap-3 p-4 flex-wrap">
              <button
                className={`flex h-10 shrink-0 items-center justify-center gap-x-2 rounded-full pl-5 pr-5 cursor-pointer transition-colors ${
                  activeFilter === 'all'
                    ? 'bg-primary text-background-dark font-bold'
                    : 'bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600'
                }`}
                onClick={() => filterContent('all')}
              >
                <p className="text-sm">전체</p>
              </button>
              <button
                className={`flex h-10 shrink-0 items-center justify-center gap-x-2 rounded-full pl-5 pr-5 cursor-pointer transition-colors ${
                  activeFilter === 'image'
                    ? 'bg-primary text-background-dark font-bold'
                    : 'bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600'
                }`}
                onClick={() => filterContent('image')}
              >
                <p className="text-sm">이미지</p>
              </button>
              <button
                className={`flex h-10 shrink-0 items-center justify-center gap-x-2 rounded-full pl-5 pr-5 cursor-pointer transition-colors ${
                  activeFilter === 'music'
                    ? 'bg-primary text-background-dark font-bold'
                    : 'bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600'
                }`}
                onClick={() => filterContent('music')}
              >
                <p className="text-sm">음악</p>
              </button>
              <button
                className={`flex h-10 shrink-0 items-center justify-center gap-x-2 rounded-full pl-5 pr-5 cursor-pointer transition-colors ${
                  activeFilter === 'video'
                    ? 'bg-primary text-background-dark font-bold'
                    : 'bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600'
                }`}
                onClick={() => filterContent('video')}
              >
                <p className="text-sm">비디오</p>
              </button>
            </div>

            {/* Content Sections */}
            {(activeFilter === 'all' || activeFilter === 'image') && (
              <div className="content-section">
                <div className="flex justify-between items-center px-4 pb-3 pt-8">
                  <h2 className="text-2xl font-bold">인기 이미지</h2>
                  <button className="text-sm font-bold text-primary hover:underline">모두 보기</button>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 p-4">
                  <div className="bg-gray-200 dark:bg-gray-700 rounded-lg aspect-[3/4]"></div>
                  <div className="bg-gray-200 dark:bg-gray-700 rounded-lg aspect-[3/4]"></div>
                  <div className="bg-gray-200 dark:bg-gray-700 rounded-lg aspect-[3/4]"></div>
                  <div className="bg-gray-200 dark:bg-gray-700 rounded-lg aspect-[3/4]"></div>
                </div>
              </div>
            )}

            {(activeFilter === 'all' || activeFilter === 'music') && (
              <div className="content-section">
                <div className="flex justify-between items-center px-4 pb-3 pt-8">
                  <h2 className="text-2xl font-bold">인기 음악</h2>
                  <button className="text-sm font-bold text-primary hover:underline">모두 보기</button>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 p-4">
                  <div className="bg-gray-200 dark:bg-gray-700 rounded-lg aspect-square"></div>
                  <div className="bg-gray-200 dark:bg-gray-700 rounded-lg aspect-square"></div>
                  <div className="bg-gray-200 dark:bg-gray-700 rounded-lg aspect-square"></div>
                  <div className="bg-gray-200 dark:bg-gray-700 rounded-lg aspect-square"></div>
                </div>
              </div>
            )}

            {(activeFilter === 'all' || activeFilter === 'video') && (
              <div className="content-section">
                <div className="flex justify-between items-center px-4 pb-3 pt-8">
                  <h2 className="text-2xl font-bold">인기 비디오</h2>
                  <button className="text-sm font-bold text-primary hover:underline">모두 보기</button>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4 p-4">
                  <div className="bg-gray-200 dark:bg-gray-700 rounded-lg aspect-video"></div>
                  <div className="bg-gray-200 dark:bg-gray-700 rounded-lg aspect-video"></div>
                  <div className="bg-gray-200 dark:bg-gray-700 rounded-lg aspect-video"></div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
