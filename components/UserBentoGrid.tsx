'use client';

import React from 'react';

interface UserBentoGridProps {
  pendingCount: number;
  myPromisesCount: number;
  incomingCount: number;
  stagedCount: number;
  activeFilter?: 'all' | 'outgoing' | 'incoming' | 'staged';
  onSelectFilter?: (filter: 'all' | 'outgoing' | 'incoming' | 'staged') => void;
}

export const UserBentoGrid: React.FC<UserBentoGridProps> = ({
  pendingCount,
  myPromisesCount,
  incomingCount,
  stagedCount,
  activeFilter,
  onSelectFilter,
}) => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-5">
      {/* Card 1: Needs Review */}
      <button
        type="button"
        onClick={() => onSelectFilter?.('all')}
        className={`text-left bg-white dark:bg-black border rounded-xl p-4 sm:p-5 shadow-xs transition-all cursor-pointer ${
          activeFilter === 'all'
            ? 'border-black dark:border-white ring-1 ring-black dark:ring-white'
            : 'border-[#E5E7EB] dark:border-[#27272A] hover:border-black dark:hover:border-white'
        }`}
      >
        <div className="text-[11px] font-semibold uppercase tracking-wider text-black/65 dark:text-white/65 mb-2">
          Needs Review
        </div>
        <div className="text-[22px] font-bold text-black dark:text-white mb-1 tracking-tight">
          {pendingCount} Pending
        </div>
        <div className="text-[12px] text-black/65 dark:text-white/65">
          Spoken commitments ready for your approval
        </div>
      </button>

      {/* Card 2: Promises I Made */}
      <button
        type="button"
        onClick={() => onSelectFilter?.('outgoing')}
        className={`text-left bg-white dark:bg-black border rounded-xl p-4 sm:p-5 shadow-xs transition-all cursor-pointer ${
          activeFilter === 'outgoing'
            ? 'border-black dark:border-white ring-1 ring-black dark:ring-white'
            : 'border-[#E5E7EB] dark:border-[#27272A] hover:border-black dark:hover:border-white'
        }`}
      >
        <div className="text-[11px] font-semibold uppercase tracking-wider text-blue-600 dark:text-sky-400 mb-2">
          I Promised
        </div>
        <div className="text-[22px] font-bold text-black dark:text-white mb-1 tracking-tight">
          {myPromisesCount} Outgoing
        </div>
        <div className="text-[12px] text-black/65 dark:text-white/65">
          Deliverables you promised to others
        </div>
      </button>

      {/* Card 3: Promises to Me */}
      <button
        type="button"
        onClick={() => onSelectFilter?.('incoming')}
        className={`text-left bg-white dark:bg-black border rounded-xl p-4 sm:p-5 shadow-xs transition-all cursor-pointer ${
          activeFilter === 'incoming'
            ? 'border-black dark:border-white ring-1 ring-black dark:ring-white'
            : 'border-[#E5E7EB] dark:border-[#27272A] hover:border-black dark:hover:border-white'
        }`}
      >
        <div className="text-[11px] font-semibold uppercase tracking-wider text-emerald-600 dark:text-emerald-400 mb-2">
          Promised to Me
        </div>
        <div className="text-[22px] font-bold text-black dark:text-white mb-1 tracking-tight">
          {incomingCount} Incoming
        </div>
        <div className="text-[12px] text-black/65 dark:text-white/65">
          Deliverables others promised to send you
        </div>
      </button>

      {/* Card 4: Staged Safely */}
      <button
        type="button"
        onClick={() => onSelectFilter?.('staged')}
        className={`text-left bg-white dark:bg-black border rounded-xl p-4 sm:p-5 shadow-xs transition-all cursor-pointer ${
          activeFilter === 'staged'
            ? 'border-black dark:border-white ring-1 ring-black dark:ring-white'
            : 'border-[#E5E7EB] dark:border-[#27272A] hover:border-black dark:hover:border-white'
        }`}
      >
        <div className="text-[11px] font-semibold uppercase tracking-wider text-black/65 dark:text-white/65 mb-2">
          Staged to Apps
        </div>
        <div className="text-[22px] font-bold text-black dark:text-white mb-1 tracking-tight">
          {stagedCount} Protected
        </div>
        <div className="text-[12px] text-black/65 dark:text-white/65">
          Safely staged in Gmail, Calendar &amp; Todoist
        </div>
      </button>
    </div>
  );
};
