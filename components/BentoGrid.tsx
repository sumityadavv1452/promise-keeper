'use client';

import React from 'react';

interface BentoGridProps {
  latencyMs: number;
  tokensUsed: number;
  estimatedCost: number;
  pendingCount: number;
  stagedCount: number;
}

export const BentoGrid: React.FC<BentoGridProps> = ({
  latencyMs,
  tokensUsed,
  estimatedCost,
  pendingCount,
  stagedCount,
}) => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-5">
      {/* Card 1: BEE AUDIO INGESTION */}
      <div className="bg-white dark:bg-black border border-[#E5E7EB] dark:border-[#27272A] rounded-xl p-4 sm:p-5 shadow-xs hover:border-black dark:hover:border-white transition-colors">
        <div className="text-[11px] font-semibold uppercase tracking-wider text-black/65 dark:text-white/65 mb-2">
          Bee Audio Ingestion
        </div>
        <div className="text-[22px] font-bold text-black dark:text-white mb-1 tracking-tight">
          Active Stream
        </div>
        <div className="text-[12px] text-black/65 dark:text-white/65">
          Sync: 5s · Diarized 16kHz
        </div>
      </div>

      {/* Card 2: INFERENCE LATENCY */}
      <div className="bg-white dark:bg-black border border-[#E5E7EB] dark:border-[#27272A] rounded-xl p-4 sm:p-5 shadow-xs hover:border-black dark:hover:border-white transition-colors">
        <div className="text-[11px] font-semibold uppercase tracking-wider text-black/65 dark:text-white/65 mb-2">
          Inference Latency
        </div>
        <div className="text-[22px] font-bold text-black dark:text-white mb-1 tracking-tight font-mono tabular-nums">
          {latencyMs} ms
        </div>
        <div className="text-[12px] text-black/65 dark:text-white/65">
          Bedrock Converse API
        </div>
      </div>

      {/* Card 3: TOKEN UTILIZATION */}
      <div className="bg-white dark:bg-black border border-[#E5E7EB] dark:border-[#27272A] rounded-xl p-4 sm:p-5 shadow-xs hover:border-black dark:hover:border-white transition-colors">
        <div className="text-[11px] font-semibold uppercase tracking-wider text-black/65 dark:text-white/65 mb-2">
          Token Utilization
        </div>
        <div className="text-[22px] font-bold text-black dark:text-white mb-1 tracking-tight font-mono tabular-nums">
          {tokensUsed.toLocaleString()} tokens
        </div>
        <div className="text-[12px] text-black/65 dark:text-white/65">
          ${estimatedCost.toFixed(4)} USD · Nova Pro
        </div>
      </div>

      {/* Card 4: STAGED PIPELINE */}
      <div className="bg-white dark:bg-black border border-[#E5E7EB] dark:border-[#27272A] rounded-xl p-4 sm:p-5 shadow-xs hover:border-black dark:hover:border-white transition-colors">
        <div className="text-[11px] font-semibold uppercase tracking-wider text-black/65 dark:text-white/65 mb-2">
          Staged Pipeline
        </div>
        <div className="text-[22px] font-bold text-black dark:text-white mb-1 tracking-tight font-mono tabular-nums">
          {pendingCount} Pending
        </div>
        <div className="text-[12px] text-black/65 dark:text-white/65">
          0 overdue · {stagedCount} staged safely
        </div>
      </div>
    </div>
  );
};
