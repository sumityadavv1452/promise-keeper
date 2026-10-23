'use client';

import React from 'react';
import { GmailIcon, CalendarIcon, TodoistIcon, CheckIcon, PulseDot } from './icons';

export const UserSidebar: React.FC = () => {
  return (
    <aside className="w-full md:w-[260px] shrink-0 flex flex-col gap-5">
      {/* 1. Safe Staging Guarantee */}
      <div>
        <div className="text-[11.5px] font-bold uppercase tracking-wider text-black dark:text-white mb-2">
          Safety Guarantees
        </div>
        <div className="bg-white dark:bg-black border border-[#E5E7EB] dark:border-[#27272A] rounded-xl p-3.5 flex flex-col gap-2.5 text-[12.5px] shadow-xs">
          <div className="flex items-start gap-2">
            <CheckIcon className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400 shrink-0 mt-0.5" />
            <div className="text-black/80 dark:text-white/80 leading-snug">
              <strong className="text-black dark:text-white font-semibold">Zero Auto-Send:</strong> Emails are saved exclusively as Gmail drafts for your manual review.
            </div>
          </div>

          <div className="flex items-start gap-2 pt-2 border-t border-[#E5E7EB] dark:border-[#27272A]">
            <CheckIcon className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400 shrink-0 mt-0.5" />
            <div className="text-black/80 dark:text-white/80 leading-snug">
              <strong className="text-black dark:text-white font-semibold">Tentative Holds:</strong> Calendar events won&apos;t double-book or overwrite existing meetings.
            </div>
          </div>

          <div className="flex items-start gap-2 pt-2 border-t border-[#E5E7EB] dark:border-[#27272A]">
            <CheckIcon className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400 shrink-0 mt-0.5" />
            <div className="text-black/80 dark:text-white/80 leading-snug">
              <strong className="text-black dark:text-white font-semibold">#promise-keeper:</strong> Tasks in Todoist are pre-tagged for effortless tracking.
            </div>
          </div>
        </div>
      </div>

      {/* 2. Destination Apps */}
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

      {/* 3. Connected Hardware */}
      <div>
        <div className="text-[11.5px] font-bold uppercase tracking-wider text-black dark:text-white mb-2">
          Hardware Status
        </div>
        <div className="bg-white dark:bg-black border border-[#E5E7EB] dark:border-[#27272A] rounded-xl p-3.5 flex flex-col gap-2 text-[12.5px] shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-black/65 dark:text-white/65">Bee Wearable</span>
            <span className="inline-flex items-center gap-1.5 text-emerald-600 dark:text-emerald-400 font-semibold">
              <PulseDot />
              <span>Connected</span>
            </span>
          </div>
          <div className="flex items-center justify-between text-black/65 dark:text-white/65">
            <span>Audio Stream</span>
            <span className="text-black dark:text-white font-medium">16kHz High-Fidelity</span>
          </div>
          <div className="flex items-center justify-between text-black/65 dark:text-white/65">
            <span>Battery</span>
            <span className="text-black dark:text-white font-medium">94% Charged</span>
          </div>
        </div>
      </div>
    </aside>
  );
};
