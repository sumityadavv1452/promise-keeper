'use client';

import React from 'react';

interface ActionRowProps {
  onSyncBee: () => void;
  onStageAll: () => void;
  onResetPipeline: () => void;
  isSyncing?: boolean;
  mode?: 'user' | 'dev';
}

export const ActionRow: React.FC<ActionRowProps> = ({
  onSyncBee,
  onStageAll,
  onResetPipeline,
  isSyncing = false,
  mode = 'user',
}) => {
  return (
    <div className="flex items-center gap-3 mb-5 flex-wrap sm:flex-nowrap">
      {mode === 'user' ? (
        <>
          <button
            onClick={onStageAll}
            className="h-[36px] px-5 bg-black dark:bg-white text-white dark:text-black font-semibold rounded-lg text-[13px] shadow-xs hover:opacity-90 transition-all whitespace-nowrap cursor-pointer active:scale-[0.98]"
          >
            Approve & Stage All
          </button>

          <button
            onClick={onSyncBee}
            disabled={isSyncing}
            className="h-[36px] px-5 bg-white dark:bg-black border border-black/20 dark:border-[#27272A] rounded-lg text-[13px] font-medium text-black dark:text-white shadow-xs hover:border-black dark:hover:border-white hover:bg-black hover:text-white dark:hover:bg-white dark:hover:text-black transition-all whitespace-nowrap disabled:opacity-50 cursor-pointer active:scale-[0.98]"
          >
            Sync with Bee
          </button>

          <button
            onClick={onResetPipeline}
            className="h-[36px] px-4 bg-white dark:bg-black border border-black/20 dark:border-[#27272A] rounded-lg text-[13px] font-medium text-black/60 dark:text-white/60 shadow-xs hover:border-black dark:hover:border-white hover:text-black dark:hover:text-white transition-all whitespace-nowrap cursor-pointer active:scale-[0.98]"
          >
            Reset
          </button>
        </>
      ) : (
        <>
          <button
            onClick={onSyncBee}
            disabled={isSyncing}
            className="h-[36px] px-5 bg-white dark:bg-black border border-black/20 dark:border-[#27272A] rounded-lg text-[13px] font-medium text-black dark:text-white shadow-xs hover:border-black dark:hover:border-white hover:bg-black hover:text-white dark:hover:bg-white dark:hover:text-black transition-all whitespace-nowrap disabled:opacity-50 cursor-pointer active:scale-[0.98]"
          >
            Sync from Bee
          </button>

          <button
            onClick={onStageAll}
            className="h-[36px] px-5 bg-white dark:bg-black border border-black/20 dark:border-[#27272A] rounded-lg text-[13px] font-medium text-black dark:text-white shadow-xs hover:border-black dark:hover:border-white hover:bg-black hover:text-white dark:hover:bg-white dark:hover:text-black transition-all whitespace-nowrap cursor-pointer active:scale-[0.98]"
          >
            Stage All Commitments
          </button>

          <button
            onClick={onResetPipeline}
            className="h-[36px] px-5 bg-white dark:bg-black border border-black/20 dark:border-[#27272A] rounded-lg text-[13px] font-medium text-black dark:text-white shadow-xs hover:border-black dark:hover:border-white hover:bg-black hover:text-white dark:hover:bg-white dark:hover:text-black transition-all whitespace-nowrap cursor-pointer active:scale-[0.98]"
          >
            Reset Pipeline
          </button>
        </>
      )}
    </div>
  );
};
