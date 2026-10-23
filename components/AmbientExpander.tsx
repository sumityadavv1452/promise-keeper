'use client';

import React, { useState } from 'react';

export const AmbientExpander: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="mb-6">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 text-[13px] font-medium text-main hover:text-blue-600 dark:hover:text-sky-400 transition-colors py-1 cursor-pointer select-none"
      >
        <span className={`text-[12px] text-muted transition-transform duration-150 inline-block ${isOpen ? 'rotate-90' : ''}`}>
          ›
        </span>
        <span>Ambient Transcript Stream (Bee Wearable Audio)</span>
      </button>

      {isOpen && (
        <div className="mt-2.5 bg-white dark:bg-black border border-[#E5E7EB] dark:border-[#27272A] rounded-xl p-4 font-mono text-[12px] text-main leading-relaxed flex flex-col gap-2 shadow-xs transition-all">
          <div>
            <span className="text-muted tabular-nums">[09:41:04]</span>{' '}
            <strong className="font-semibold text-main">Hardware:</strong> Bee Audio Stream · Diarization Active · 16kHz Sampling
          </div>
          <div>
            <span className="text-muted tabular-nums">[09:41:12]</span>{' '}
            <strong className="text-blue-600 dark:text-sky-400 font-semibold">Speaker 1 (Me):</strong> &ldquo;Hey Alex, thanks for the sync. I&apos;ll send you the revised pitch deck by 5 PM tomorrow with the updated architecture diagram.&rdquo;
          </div>
          <div>
            <span className="text-muted tabular-nums">[09:41:20]</span>{' '}
            <strong className="text-emerald-600 dark:text-emerald-400 font-semibold">Speaker 2 (Alex Rivera):</strong> &ldquo;Sounds great. Make sure to review the Q3 analytics report before Wednesday noon so we&apos;re aligned for the client sync.&rdquo;
          </div>
          <div>
            <span className="text-muted tabular-nums">[09:41:28]</span>{' '}
            <strong className="text-blue-600 dark:text-sky-400 font-semibold">Speaker 1 (Me):</strong> &ldquo;Will do, let&apos;s also block 30 minutes on Thursday morning for a dry run.&rdquo;
          </div>
          <div>
            <span className="text-muted tabular-nums">[09:41:35]</span>{' '}
            <strong className="text-emerald-600 dark:text-emerald-400 font-semibold">Speaker 2 (Alex Rivera):</strong> &ldquo;Perfect, calendar invite received. Looking forward to it.&rdquo;
          </div>
        </div>
      )}
    </div>
  );
};
