'use client';

import React from 'react';
import { SparkleStar, RefreshIcon, UserIcon, CodeIcon } from './icons';

interface NavbarProps {
  mode: 'user' | 'dev';
  setMode: (mode: 'user' | 'dev') => void;
  activeView: 'commitments' | 'stream';
  setActiveView: (view: 'commitments' | 'stream') => void;
  userFilter: 'all' | 'outgoing' | 'incoming' | 'staged';
  setUserFilter: (filter: 'all' | 'outgoing' | 'incoming' | 'staged') => void;
  onSync: () => void;
  isSyncing?: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  mode,
  setMode,
  activeView,
  setActiveView,
  userFilter,
  setUserFilter,
  onSync,
  isSyncing = false,
}) => {
  return (
    <header className="w-full bg-white dark:bg-black border border-[#E5E7EB] dark:border-[#27272A] rounded-xl px-5 py-3.5 shadow-sm mb-5 transition-colors duration-150">
      <div className="flex items-center justify-between gap-4 flex-wrap sm:flex-nowrap">
        {/* Left: Branding & Tagline */}
        <div className="flex flex-col justify-center min-w-[300px]">
          <div className="flex items-center gap-2.5 whitespace-nowrap">
            <h1 className="text-[18px] font-bold tracking-tight text-black dark:text-white inline-flex items-center gap-2">
              <SparkleStar className="w-4 h-4 text-black dark:text-white" />
              <span>Promise Keeper</span>
            </h1>
            <span className="font-mono text-[11.5px] font-medium bg-white dark:bg-black text-black dark:text-white px-2.5 py-0.5 rounded-full border border-black/15 dark:border-[#27272A]">
              {mode === 'user' ? 'Bee Connected · Everyday AI' : 'Bee v1.4.2 · Bedrock Nova Pro'}
            </span>
          </div>
          <p className="text-[12px] text-black/60 dark:text-white/60 leading-tight mt-0.5">
            &ldquo;You said it. We&apos;ll remember it.&rdquo;
          </p>
        </div>

        {/* Right: Controls & Actions */}
        <div className="flex items-center gap-3 shrink-0 flex-wrap sm:flex-nowrap">
          {/* Middle Switcher: User Filter vs Dev View Switcher */}
          {mode === 'user' ? (
            <div className="bg-white dark:bg-black border border-black/15 dark:border-[#27272A] rounded-full p-[2px] flex items-center h-[32px] box-border select-none">
              <button
                type="button"
                onClick={() => setUserFilter('all')}
                className={`h-[28px] px-3.5 rounded-full text-[12px] font-medium transition-all duration-150 whitespace-nowrap cursor-pointer ${
                  userFilter === 'all'
                    ? 'bg-black dark:bg-white text-white dark:text-black font-semibold shadow-xs'
                    : 'text-black/60 dark:text-white/60 hover:text-black dark:hover:text-white'
                }`}
              >
                All
              </button>
              <button
                type="button"
                onClick={() => setUserFilter('outgoing')}
                className={`h-[28px] px-3.5 rounded-full text-[12px] font-medium transition-all duration-150 whitespace-nowrap cursor-pointer ${
                  userFilter === 'outgoing'
                    ? 'bg-black dark:bg-white text-white dark:text-black font-semibold shadow-xs'
                    : 'text-black/60 dark:text-white/60 hover:text-black dark:hover:text-white'
                }`}
              >
                I Promised
              </button>
              <button
                type="button"
                onClick={() => setUserFilter('incoming')}
                className={`h-[28px] px-3.5 rounded-full text-[12px] font-medium transition-all duration-150 whitespace-nowrap cursor-pointer ${
                  userFilter === 'incoming'
                    ? 'bg-black dark:bg-white text-white dark:text-black font-semibold shadow-xs'
                    : 'text-black/60 dark:text-white/60 hover:text-black dark:hover:text-white'
                }`}
              >
                Promised to Me
              </button>
              <button
                type="button"
                onClick={() => setUserFilter('staged')}
                className={`h-[28px] px-3.5 rounded-full text-[12px] font-medium transition-all duration-150 whitespace-nowrap cursor-pointer ${
                  userFilter === 'staged'
                    ? 'bg-black dark:bg-white text-white dark:text-black font-semibold shadow-xs'
                    : 'text-black/60 dark:text-white/60 hover:text-black dark:hover:text-white'
                }`}
              >
                Staged
              </button>
            </div>
          ) : (
            <div className="bg-white dark:bg-black border border-black/15 dark:border-[#27272A] rounded-full p-[2px] flex items-center h-[32px] box-border select-none">
              <button
                type="button"
                onClick={() => setActiveView('commitments')}
                className={`h-[28px] px-3.5 rounded-full text-[12px] font-medium transition-all duration-150 whitespace-nowrap cursor-pointer ${
                  activeView === 'commitments'
                    ? 'bg-black dark:bg-white text-white dark:text-black font-semibold shadow-xs'
                    : 'text-black/60 dark:text-white/60 hover:text-black dark:hover:text-white'
                }`}
              >
                Commitments
              </button>
              <button
                type="button"
                onClick={() => setActiveView('stream')}
                className={`h-[28px] px-3.5 rounded-full text-[12px] font-medium transition-all duration-150 whitespace-nowrap cursor-pointer ${
                  activeView === 'stream'
                    ? 'bg-black dark:bg-white text-white dark:text-black font-semibold shadow-xs'
                    : 'text-black/60 dark:text-white/60 hover:text-black dark:hover:text-white'
                }`}
              >
                Transcript Stream
              </button>
            </div>
          )}

          {/* Mint Live Badge */}
          <div className="bg-[#ECFDF5] dark:bg-emerald-950/40 border border-[#A7F3D0] dark:border-emerald-800/60 text-[#059669] dark:text-[#34D399] rounded-full px-2.5 py-1 text-[11.5px] font-semibold flex items-center gap-1.5 shrink-0 select-none">
            <span className="w-2 h-2 rounded-full bg-[#10B981] shrink-0 inline-block"></span>
            <span>Live</span>
          </div>

          {/* Persona Mode Toggle Capsule: User vs Developer */}
          <div
            role="group"
            aria-label="User or Developer Mode Toggle"
            className="h-[32px] p-[2px] rounded-full bg-white dark:bg-black border border-black/15 dark:border-[#27272A] flex items-center gap-0.5 shrink-0 select-none shadow-2xs"
          >
            <button
              type="button"
              onClick={() => setMode('user')}
              className={`h-[26px] px-3 rounded-full flex items-center gap-1.5 text-[12px] font-medium transition-all cursor-pointer ${
                mode === 'user'
                  ? 'bg-black dark:bg-white text-white dark:text-black font-semibold shadow-xs'
                  : 'text-black/60 dark:text-white/60 hover:text-black dark:hover:text-white'
              }`}
              title="User Mode (Concise, concrete & jargon-free)"
            >
              <UserIcon className="w-3.5 h-3.5" />
              <span>User</span>
            </button>
            <button
              type="button"
              onClick={() => setMode('dev')}
              className={`h-[26px] px-3 rounded-full flex items-center gap-1.5 text-[12px] font-medium transition-all cursor-pointer ${
                mode === 'dev'
                  ? 'bg-black dark:bg-white text-white dark:text-black font-semibold shadow-xs'
                  : 'text-black/60 dark:text-white/60 hover:text-black dark:hover:text-white'
              }`}
              title="Developer Mode (Telemetry, models & daemon)"
            >
              <CodeIcon className="w-3.5 h-3.5" />
              <span>Dev</span>
            </button>
          </div>

          {/* Sync Action Button */}
          <button
            onClick={onSync}
            disabled={isSyncing}
            className="h-[32px] px-3.5 bg-black dark:bg-white text-white dark:text-black text-[13px] font-semibold rounded-lg flex items-center justify-center gap-1.5 shadow-sm hover:opacity-90 active:scale-95 transition-all whitespace-nowrap shrink-0 disabled:opacity-50 cursor-pointer"
          >
            <RefreshIcon className={`w-3.5 h-3.5 ${isSyncing ? 'animate-spin' : ''}`} />
            <span>{mode === 'user' ? 'Sync with Bee' : 'Sync Stream'}</span>
          </button>
        </div>
      </div>
    </header>
  );
};
