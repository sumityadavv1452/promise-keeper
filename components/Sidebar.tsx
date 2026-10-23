'use client';

import React from 'react';
import { GmailIcon, CalendarIcon, TodoistIcon, ChevronDownIcon } from './icons';

interface SidebarProps {
  selectedModel: string;
  setSelectedModel: (model: string) => void;
  latencyMs: number;
  tokensUsed: number;
  estimatedCost: number;
}

export const Sidebar: React.FC<SidebarProps> = ({
  selectedModel,
  setSelectedModel,
  latencyMs,
  tokensUsed,
  estimatedCost,
}) => {
  return (
    <aside className="w-full md:w-[260px] shrink-0 flex flex-col gap-5">
      {/* 1. Runtime Daemon Panel */}
      <div>
        <div className="text-[11.5px] font-bold uppercase tracking-wider text-black dark:text-white mb-2">
          Runtime Daemon
        </div>
        <div className="bg-white dark:bg-black border border-[#E5E7EB] dark:border-[#27272A] rounded-xl p-3.5 flex flex-col gap-2.5 text-[13px] shadow-xs">
          <div className="flex items-center justify-between pb-2 border-b border-[#E5E7EB] dark:border-[#27272A]">
            <span className="text-black/65 dark:text-white/65">Daemon Status</span>
            <span className="inline-flex items-center gap-1.5 text-emerald-600 dark:text-emerald-400 font-semibold text-[12px]">
              <span className="w-2 h-2 rounded-full bg-[#10B981] shrink-0 inline-block"></span>
              <span>Active</span>
            </span>
          </div>

          <div className="flex items-center justify-between pb-2 border-b border-[#E5E7EB] dark:border-[#27272A]">
            <span className="text-black/65 dark:text-white/65">CLI Bridge</span>
            <span className="font-mono text-[12px] text-black dark:text-white font-medium">bee CLI / MCP</span>
          </div>

          <div className="flex items-center justify-between pb-2 border-b border-[#E5E7EB] dark:border-[#27272A]">
            <span className="text-black/65 dark:text-white/65">Ingestion Mode</span>
            <span className="font-mono text-[12px] font-semibold text-black dark:text-white">Offline Cache</span>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-black/65 dark:text-white/65">Audio Diarization</span>
            <span className="font-mono text-[12px] font-semibold text-emerald-600 dark:text-emerald-400">16kHz Active</span>
          </div>
        </div>
      </div>

      {/* 2. Bedrock Inference Model Selector */}
      <div>
        <div className="text-[11.5px] font-bold uppercase tracking-wider text-black dark:text-white mb-2">
          Bedrock Inference Model
        </div>
        <div className="relative flex items-center">
          <select
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
            className="w-full h-[40px] bg-white dark:bg-black border border-black dark:border-[#3F3F46] rounded-lg px-3.5 pr-11 text-[13px] text-black dark:text-white appearance-none focus:outline-none font-mono font-medium shadow-xs cursor-pointer transition-colors"
          >
            <option value="amazon.nova-pro-v1:0" className="bg-white dark:bg-black text-black dark:text-white">amazon.nova-pro-v1:0</option>
            <option value="anthropic.claude-3-5-sonnet-20241022-v2:0" className="bg-white dark:bg-black text-black dark:text-white">
              anthropic.claude-3-5-sonnet-20241022-v2:0
            </option>
          </select>
          <div className="pointer-events-none absolute right-1.5 inset-y-0 my-auto w-7 h-7 bg-black dark:bg-white text-white dark:text-black rounded-md flex items-center justify-center shadow-xs">
            <ChevronDownIcon className="w-3.5 h-3.5 text-white dark:text-black" strokeWidth={2.5} />
          </div>
        </div>
      </div>

      {/* 3. Staging Destinations */}
      <div>
        <div className="text-[11.5px] font-bold uppercase tracking-wider text-black dark:text-white mb-2">
          Staging Destinations
        </div>
        <div className="bg-white dark:bg-black border border-[#E5E7EB] dark:border-[#27272A] rounded-xl p-3.5 flex flex-col gap-3 shadow-xs">
          <a
            href="https://mail.google.com/mail/u/0/#drafts"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2.5 text-[13.5px] font-medium text-blue-600 dark:text-sky-400 hover:underline"
          >
            <GmailIcon className="w-4 h-4 shrink-0" />
            <span>Open Gmail Drafts ↗</span>
          </a>

          <a
            href="https://calendar.google.com/"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2.5 text-[13.5px] font-medium text-blue-600 dark:text-sky-400 hover:underline"
          >
            <CalendarIcon className="w-4 h-4 shrink-0" />
            <span>Open Google Calendar ↗</span>
          </a>

          <a
            href="https://app.todoist.com/"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2.5 text-[13.5px] font-medium text-blue-600 dark:text-sky-400 hover:underline"
          >
            <TodoistIcon className="w-4 h-4 shrink-0" />
            <span>Open Todoist App ↗</span>
          </a>
        </div>
      </div>

      {/* 4. Telemetry Session */}
      <div>
        <div className="text-[11.5px] font-bold uppercase tracking-wider text-black dark:text-white mb-2">
          Telemetry Session
        </div>
        <div className="bg-white dark:bg-black border border-[#E5E7EB] dark:border-[#27272A] rounded-xl p-3.5 flex flex-col gap-1.5 text-[13px] text-black/65 dark:text-white/65 shadow-xs">
          <div>
            Converse Latency: <strong className="text-black dark:text-white font-mono tabular-nums font-semibold">{latencyMs} ms</strong>
          </div>
          <div>
            Tokens Consumed: <strong className="text-black dark:text-white font-mono tabular-nums font-semibold">{tokensUsed.toLocaleString()}</strong>
          </div>
          <div>
            Estimated Cost: <strong className="text-black dark:text-white font-mono tabular-nums font-semibold">${estimatedCost.toFixed(4)} USD</strong>
          </div>
        </div>
      </div>
    </aside>
  );
};
