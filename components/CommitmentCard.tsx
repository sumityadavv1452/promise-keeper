'use client';

import React, { useState, useEffect } from 'react';
import {
  GmailIcon,
  CalendarIcon,
  TodoistIcon,
  CheckIcon,
  ChevronDownIcon,
  SpeechBubbleIcon,
  EditIcon,
} from './icons';
import { CommitmentItem } from '../lib/types';
import { playWearableAudioMemo, stopAnyPlayingAudio } from '../lib/audio';
export type { CommitmentItem };

interface CommitmentCardProps {
  item: CommitmentItem;
  onUpdate: (updated: CommitmentItem) => void;
  onStage: (id: string) => void;
  onDismiss: (id: string) => void;
  isFirst?: boolean;
  mode?: 'user' | 'dev';
}

export const CommitmentCard: React.FC<CommitmentCardProps> = ({
  item,
  onUpdate,
  onStage,
  onDismiss,
  isFirst = false,
  mode = 'user',
}) => {
  // Dev mode tabs: Todoist Task, Gmail Draft, Calendar Event
  const [activeTab, setActiveTab] = useState<'todoist' | 'gmail' | 'calendar'>('todoist');
  // User mode customization expander
  const [isCustomizing, setIsCustomizing] = useState<boolean>(false);
  // Audio clip playback state
  const [isPlayingAudio, setIsPlayingAudio] = useState<boolean>(false);

  useEffect(() => {
    return () => {
      stopAnyPlayingAudio();
    };
  }, []);

  const handlePlayAudio = () => {
    if (isPlayingAudio) {
      stopAnyPlayingAudio();
      setIsPlayingAudio(false);
      return;
    }

    const textToPlay = item.quote || item.summary || item.task_title;
    playWearableAudioMemo(
      textToPlay,
      () => setIsPlayingAudio(true),
      () => setIsPlayingAudio(false)
    );
  };

  const handleToggleDestination = (key: 'gmail' | 'calendar' | 'todoist') => {
    const current = item.enabled_destinations ?? { gmail: true, calendar: true, todoist: true };
    onUpdate({
      ...item,
      enabled_destinations: {
        ...current,
        [key]: !current[key],
      },
    });
  };

  const handleTitleChange = (val: string) => {
    onUpdate({ ...item, task_title: val });
  };

  const handlePriorityChange = (val: string) => {
    onUpdate({ ...item, priority: val });
  };

  const handleSubjectChange = (val: string) => {
    onUpdate({ ...item, email_subject: val });
  };

  const handleBodyChange = (val: string) => {
    onUpdate({ ...item, email_body: val });
  };

  const handleCalTitleChange = (val: string) => {
    onUpdate({ ...item, calendar_title: val });
  };

  const handleDurationChange = (val: number) => {
    onUpdate({ ...item, calendar_duration: val });
  };

  const friendlyPriority = (priority: string) => {
    if (priority.includes('P1') || priority.toLowerCase().includes('high')) return 'High Priority';
    if (priority.includes('P3') || priority.toLowerCase().includes('low')) return 'Low Priority';
    return 'Medium Priority';
  };

  return (
    <article className="bg-white dark:bg-black border border-[#E5E7EB] dark:border-[#27272A] rounded-xl p-5 sm:p-6 mb-5 shadow-xs transition-colors duration-150">
      {/* ─────────────────────────────────────────────────────────────
          MODE: USER (Everyday Consumer App Experience)
         ───────────────────────────────────────────────────────────── */}
      {mode === 'user' ? (
        <div>
          {/* Header row: Clear badges */}
          <div className="flex items-center justify-between gap-3 flex-wrap mb-3">
            <div className="flex items-center gap-2 flex-wrap">
              {/* Direction Badge */}
              <span className={`inline-flex items-center gap-1.5 text-[11.5px] font-semibold px-2.5 py-0.5 rounded-full ${
                item.direction === 'MADE_BY_ME'
                  ? 'bg-[#E0F2FE] dark:bg-sky-950/40 text-[#0284C7] dark:text-[#38BDF8] border border-[#BAE6FD] dark:border-sky-800/40'
                  : 'bg-[#ECFDF5] dark:bg-emerald-950/40 text-[#059669] dark:text-[#34D399] border border-[#A7F3D0] dark:border-emerald-800/40'
              }`}>
                <SpeechBubbleIcon className="w-3 h-3 shrink-0" />
                <span>{item.direction === 'MADE_BY_ME' ? 'I Promised' : 'Promised to Me'}</span>
              </span>

              {/* Status Badge */}
              <span className="bg-white dark:bg-black text-black dark:text-white border border-black/20 dark:border-white/20 text-[11px] font-semibold px-2.5 py-0.5 rounded-full">
                {item.staged ? '✓ Staged to Apps' : 'Needs Review'}
              </span>

              {/* Ambiguity Warning */}
              {item.is_ambiguous && (
                <span className="bg-[#FEF3C7] dark:bg-amber-950/40 text-[#D97706] dark:text-[#FBBF24] border border-[#FDE68A] dark:border-amber-800/40 text-[11px] font-semibold px-2.5 py-0.5 rounded-full">
                  ⚠️ Check Details (Tentative)
                </span>
              )}

              {isFirst && !item.staged && (
                <span className="bg-[#EFF6FF] dark:bg-blue-950/40 text-[#2563EB] dark:text-[#93C5FD] border border-[#DBEAFE] dark:border-blue-800/40 text-[11px] font-semibold px-2.5 py-0.5 rounded-full">
                  Next Due
                </span>
              )}
            </div>

            {/* Deadline */}
            <div className="text-[13px] text-[#52525B] dark:text-[#A1A1AA]">
              Due: <strong className="text-black dark:text-white font-semibold">{item.verbal_deadline}</strong>
            </div>
          </div>

          {/* Promise Title */}
          <h3 className="text-[19px] font-bold text-black dark:text-white tracking-tight mb-1.5">
            {item.task_title}
          </h3>

          {/* Summary */}
          <p className="text-[14px] text-[#52525B] dark:text-[#A1A1AA] leading-relaxed mb-3">
            {item.summary}
          </p>

          {/* Counterparty Attribution */}
          <div className="text-[13px] text-[#52525B] dark:text-[#A1A1AA] mb-3.5 flex items-center gap-2 flex-wrap">
            <span>With <strong className="text-black dark:text-white font-semibold">{item.counterparty_name}</strong></span>
            <span>·</span>
            <span className="text-blue-600 dark:text-sky-400 hover:underline cursor-pointer">{item.counterparty_email}</span>
          </div>

          {/* Spoken Quote Bubble */}
          {item.quote && (
            <div className="mb-4 p-3.5 bg-[#F9FAFB] dark:bg-[#0A0A0A] border border-[#E5E7EB] dark:border-[#27272A] rounded-xl text-[13px] leading-relaxed text-black/85 dark:text-white/85">
              <div className="flex items-start gap-2.5">
                <SpeechBubbleIcon className="w-4 h-4 text-black/40 dark:text-white/40 shrink-0 mt-0.5" />
                <div className="flex-1">
                  <p className="italic font-normal">
                    &ldquo;{item.quote}&rdquo;
                  </p>
                  <div className="mt-2.5 flex items-center justify-between gap-3 flex-wrap">
                    <span className="text-[11.5px] text-[#71717A] dark:text-[#A1A1AA] not-italic">
                      Recorded via Bee · {item.captured_at || 'Today'}
                    </span>

                    <button
                      type="button"
                      onClick={handlePlayAudio}
                      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-medium transition-all cursor-pointer shadow-2xs ${
                        isPlayingAudio
                          ? 'bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-400 dark:border-emerald-600 text-emerald-800 dark:text-emerald-300'
                          : 'bg-white dark:bg-black border border-black/15 dark:border-white/20 text-black dark:text-white hover:border-black dark:hover:border-white'
                      }`}
                      title={isPlayingAudio ? 'Click to stop audio' : 'Listen to captured wearable audio'}
                    >
                      {isPlayingAudio ? (
                        <>
                          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                          <span className="font-mono font-bold">Playing Audio</span>
                          <span className="text-emerald-600 dark:text-emerald-400 tracking-wider text-[10px] font-mono animate-pulse">ılı·llı·lı</span>
                          <span className="text-[10px] opacity-75">✕ Stop</span>
                        </>
                      ) : (
                        <>
                          <span className="text-[10px]">▶</span>
                          <span>Play Audio ({item.audio_duration_seconds || 8}s)</span>
                        </>
                      )}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Ambiguity Explanation if Ambiguous */}
          {item.is_ambiguous && (
            <div className="mb-4 p-3 bg-amber-50/60 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-800/40 rounded-lg text-[12.5px] text-amber-800 dark:text-amber-300">
              <strong className="font-semibold">Gentle check:</strong> This sounded like a casual or tentative mention (&ldquo;maybe I&apos;ll pass along...&rdquo;). Tap <strong>Approve &amp; Save</strong> if you still want to hold time for it, or <strong>Dismiss</strong> if it was just casual chit-chat.
            </div>
          )}

          {/* Prepared Staging Actions Strip (Clear, intuitive, no tabs) */}
          <div className="mb-4 bg-white dark:bg-black border border-[#E5E7EB] dark:border-[#27272A] rounded-xl p-3.5 shadow-2xs">
            <div className="text-[11.5px] font-bold uppercase tracking-wider text-black/70 dark:text-white/70 mb-2.5 flex items-center justify-between">
              <span>Ready to Stage for You:</span>
              <button
                type="button"
                onClick={() => setIsCustomizing(!isCustomizing)}
                className="text-[12px] font-medium text-blue-600 dark:text-sky-400 hover:underline flex items-center gap-1 cursor-pointer capitalize"
              >
                <EditIcon className="w-3 h-3" />
                <span>{isCustomizing ? 'Hide editor' : 'Customize details'}</span>
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-2.5 text-[12.5px]">
              {/* Email item */}
              <div className="p-2.5 rounded-lg border border-[#F3F4F6] dark:border-[#1F1F23] bg-[#FAFAFA] dark:bg-[#0D0D0E] flex flex-col justify-between">
                <div>
                  <div className="flex items-center gap-1.5 font-semibold text-black dark:text-white mb-1">
                    <GmailIcon className="w-3.5 h-3.5" />
                    <span>Gmail Draft</span>
                  </div>
                  <p className="text-[#52525B] dark:text-[#A1A1AA] text-[12px] line-clamp-2">
                    {item.email_subject || `Follow up: ${item.task_title}`}
                  </p>
                </div>
                <div className="mt-2 text-[11px] text-emerald-600 dark:text-emerald-400 font-medium">
                  ✓ Never auto-sent (Draft only)
                </div>
              </div>

              {/* Calendar item */}
              <div className="p-2.5 rounded-lg border border-[#F3F4F6] dark:border-[#1F1F23] bg-[#FAFAFA] dark:bg-[#0D0D0E] flex flex-col justify-between">
                <div>
                  <div className="flex items-center gap-1.5 font-semibold text-black dark:text-white mb-1">
                    <CalendarIcon className="w-3.5 h-3.5" />
                    <span>Google Calendar</span>
                  </div>
                  <p className="text-black dark:text-white font-medium text-[12px] line-clamp-1">
                    {item.recommended_time_slot || `${item.calendar_duration || 30}-min focus hold`}
                  </p>
                  <p className="text-[#71717A] dark:text-[#A1A1AA] text-[11px] mt-0.5">
                    Buffer before {item.verbal_deadline}
                  </p>
                </div>
                <div className="mt-2 text-[11px] text-emerald-600 dark:text-emerald-400 font-medium">
                  ✓ Won&apos;t double-book
                </div>
              </div>

              {/* Todoist item */}
              <div className="p-2.5 rounded-lg border border-[#F3F4F6] dark:border-[#1F1F23] bg-[#FAFAFA] dark:bg-[#0D0D0E] flex flex-col justify-between">
                <div>
                  <div className="flex items-center gap-1.5 font-semibold text-black dark:text-white mb-1">
                    <TodoistIcon className="w-3.5 h-3.5" />
                    <span>Todoist Task</span>
                  </div>
                  <p className="text-[#52525B] dark:text-[#A1A1AA] text-[12px] line-clamp-2">
                    {friendlyPriority(item.priority)}
                  </p>
                </div>
                <div className="mt-2 text-[11px] text-emerald-600 dark:text-emerald-400 font-medium">
                  ✓ Tagged #promise-keeper
                </div>
              </div>
            </div>
          </div>

          {/* User Mode Customization Drawer (when toggled) */}
          {isCustomizing && (
            <div className="mb-4 p-4 border border-black dark:border-white rounded-xl bg-white dark:bg-black space-y-3.5 transition-all">
              <div className="text-[12.5px] font-bold text-black dark:text-white flex items-center justify-between border-b border-[#E5E7EB] dark:border-[#27272A] pb-2">
                <span>Customize Details Before Approving</span>
                <span className="text-[11px] font-normal text-[#52525B] dark:text-[#A1A1AA]">
                  Changes will be saved into your Gmail draft &amp; Calendar
                </span>
              </div>

              {/* Destination Toggles */}
              <div>
                <label className="block text-[11.5px] font-semibold text-[#52525B] dark:text-[#A1A1AA] mb-1.5">
                  Save to Destinations:
                </label>
                <div className="flex items-center gap-2 flex-wrap">
                  <button
                    type="button"
                    onClick={() => handleToggleDestination('gmail')}
                    className={`h-[28px] px-3 rounded-full text-[12px] font-medium flex items-center gap-1.5 transition-all cursor-pointer ${
                      (item.enabled_destinations?.gmail ?? true)
                        ? 'bg-black dark:bg-white text-white dark:text-black font-semibold shadow-xs'
                        : 'bg-white dark:bg-black text-[#71717A] border border-[#E5E7EB] dark:border-[#27272A]'
                    }`}
                  >
                    <GmailIcon className="w-3.5 h-3.5" />
                    <span>Gmail Draft {(item.enabled_destinations?.gmail ?? true) ? '✓' : ''}</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => handleToggleDestination('calendar')}
                    className={`h-[28px] px-3 rounded-full text-[12px] font-medium flex items-center gap-1.5 transition-all cursor-pointer ${
                      (item.enabled_destinations?.calendar ?? true)
                        ? 'bg-black dark:bg-white text-white dark:text-black font-semibold shadow-xs'
                        : 'bg-white dark:bg-black text-[#71717A] border border-[#E5E7EB] dark:border-[#27272A]'
                    }`}
                  >
                    <CalendarIcon className="w-3.5 h-3.5" />
                    <span>Calendar Hold {(item.enabled_destinations?.calendar ?? true) ? '✓' : ''}</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => handleToggleDestination('todoist')}
                    className={`h-[28px] px-3 rounded-full text-[12px] font-medium flex items-center gap-1.5 transition-all cursor-pointer ${
                      (item.enabled_destinations?.todoist ?? true)
                        ? 'bg-black dark:bg-white text-white dark:text-black font-semibold shadow-xs'
                        : 'bg-white dark:bg-black text-[#71717A] border border-[#E5E7EB] dark:border-[#27272A]'
                    }`}
                  >
                    <TodoistIcon className="w-3.5 h-3.5" />
                    <span>Todoist Task {(item.enabled_destinations?.todoist ?? true) ? '✓' : ''}</span>
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div className="sm:col-span-2">
                  <label className="block text-[11.5px] font-semibold text-[#52525B] dark:text-[#A1A1AA] mb-1">
                    Task Title
                  </label>
                  <input
                    type="text"
                    value={item.task_title}
                    onChange={(e) => handleTitleChange(e.target.value)}
                    className="w-full h-[38px] bg-white dark:bg-black border border-black dark:border-[#3F3F46] rounded-lg px-3 text-[13px] text-black dark:text-white focus:outline-none focus:ring-1 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-[11.5px] font-semibold text-[#52525B] dark:text-[#A1A1AA] mb-1">
                    Priority
                  </label>
                  <div className="relative flex items-center">
                    <select
                      value={item.priority}
                      onChange={(e) => handlePriorityChange(e.target.value)}
                      className="w-full h-[38px] bg-white dark:bg-black border border-black dark:border-[#3F3F46] rounded-lg px-3 pr-10 text-[13px] text-black dark:text-white appearance-none focus:outline-none cursor-pointer"
                    >
                      <option value="P1 - High">High Priority</option>
                      <option value="P2 - Medium">Medium Priority</option>
                      <option value="P3 - Low">Low Priority</option>
                    </select>
                    <div className="pointer-events-none absolute right-1.5 inset-y-0 my-auto w-7 h-7 bg-black dark:bg-white text-white dark:text-black rounded-md flex items-center justify-center">
                      <ChevronDownIcon className="w-3.5 h-3.5 text-white dark:text-black" strokeWidth={2.5} />
                    </div>
                  </div>
                </div>
              </div>

              <div>
                <label className="block text-[11.5px] font-semibold text-[#52525B] dark:text-[#A1A1AA] mb-1">
                  Draft Email Message to {item.counterparty_name}
                </label>
                <textarea
                  value={
                    item.email_body ||
                    `Hi ${item.counterparty_name},\n\nJust following up on our sync. I'll take care of "${item.task_title}" by ${item.verbal_deadline}.\n\nBest,\nMe`
                  }
                  onChange={(e) => handleBodyChange(e.target.value)}
                  rows={3}
                  className="w-full bg-white dark:bg-black border border-black dark:border-[#3F3F46] rounded-lg p-3 text-[13px] text-black dark:text-white focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-[11.5px] font-semibold text-[#52525B] dark:text-[#A1A1AA] mb-1">
                    Calendar Hold Length
                  </label>
                  <div className="relative flex items-center">
                    <select
                      value={item.calendar_duration || 30}
                      onChange={(e) => handleDurationChange(Number(e.target.value))}
                      className="w-full h-[38px] bg-white dark:bg-black border border-black dark:border-[#3F3F46] rounded-lg px-3 pr-10 text-[13px] text-black dark:text-white appearance-none focus:outline-none cursor-pointer"
                    >
                      <option value={15}>15 Minutes Focus</option>
                      <option value={30}>30 Minutes Focus</option>
                      <option value={45}>45 Minutes Focus</option>
                      <option value={60}>1 Hour Focus</option>
                    </select>
                    <div className="pointer-events-none absolute right-1.5 inset-y-0 my-auto w-7 h-7 bg-black dark:bg-white text-white dark:text-black rounded-md flex items-center justify-center">
                      <ChevronDownIcon className="w-3.5 h-3.5 text-white dark:text-black" strokeWidth={2.5} />
                    </div>
                  </div>
                </div>

                <div className="flex items-end">
                  <button
                    type="button"
                    onClick={() => setIsCustomizing(false)}
                    className="h-[38px] px-4 w-full bg-white dark:bg-black border border-black/20 dark:border-white/20 hover:border-black dark:hover:border-white rounded-lg text-[12.5px] font-medium text-black dark:text-white transition-colors cursor-pointer"
                  >
                    Done Customizing
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* User Mode Actions Row */}
          <div className="flex items-center gap-3 mt-4">
            <button
              onClick={() => onStage(item.id)}
              disabled={item.staged}
              className={`h-[38px] px-5 rounded-lg text-[13px] font-semibold transition-all shadow-xs flex items-center justify-center gap-2 cursor-pointer ${
                item.staged
                  ? 'bg-white dark:bg-black border border-black/15 dark:border-white/15 text-black/40 dark:text-white/40 cursor-not-allowed'
                  : 'bg-black dark:bg-white text-white dark:text-black hover:opacity-90 active:scale-[0.98]'
              }`}
            >
              {item.staged ? '✓ Staged to Apps' : 'Approve & Save to Apps'}
            </button>

            {!item.staged && (
              <button
                type="button"
                onClick={() => setIsCustomizing(!isCustomizing)}
                className="h-[38px] px-4 rounded-lg text-[13px] font-medium text-black dark:text-white bg-white dark:bg-black border border-black/20 dark:border-[#27272A] hover:border-black dark:hover:border-white transition-all shadow-xs cursor-pointer active:scale-[0.98]"
              >
                {isCustomizing ? 'Hide Editor' : 'Customize'}
              </button>
            )}

            <button
              onClick={() => onDismiss(item.id)}
              className="h-[38px] px-4 rounded-lg text-[13px] font-medium text-[#71717A] dark:text-[#A1A1AA] hover:text-black dark:hover:text-white bg-transparent transition-all cursor-pointer active:scale-[0.98]"
            >
              Not a Promise
            </button>
          </div>

          {/* Staged Confirmation Banner */}
          {item.staged && (
            <div className="mt-3.5 p-3.5 bg-white dark:bg-black border border-emerald-500 rounded-xl text-[13px] text-emerald-700 dark:text-emerald-400 flex items-center justify-between gap-3 flex-wrap">
              <div className="flex items-center gap-2">
                <CheckIcon className="w-4 h-4 text-emerald-600 dark:text-emerald-400 shrink-0" />
                <span>
                  <strong className="font-semibold">All set:</strong> Saved to your Gmail Drafts, Google Calendar hold, and Todoist.
                </span>
              </div>
              <div className="flex items-center gap-2.5">
                <a
                  href="https://mail.google.com/mail/u/0/#drafts"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-emerald-700 dark:text-emerald-300 font-semibold underline text-[12.5px] hover:opacity-85"
                >
                  View Draft ↗
                </a>
                <span>·</span>
                <a
                  href="https://calendar.google.com/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-emerald-700 dark:text-emerald-300 font-semibold underline text-[12.5px] hover:opacity-85"
                >
                  Calendar ↗
                </a>
              </div>
            </div>
          )}
        </div>
      ) : (
        /* ─────────────────────────────────────────────────────────────
            MODE: DEV (Telemetry, Exact Scopes, Form Tabs & ISO)
           ───────────────────────────────────────────────────────────── */
        <div>
          {/* Top Header Row: Pill Chips matching reference image */}
          <div className="flex items-center justify-between gap-4 flex-wrap mb-2.5">
            <div className="flex items-center gap-2 flex-wrap">
              {/* Direction Chip */}
              <span className="bg-[#E0F2FE] dark:bg-sky-950/40 text-[#0284C7] dark:text-[#38BDF8] border border-[#BAE6FD] dark:border-sky-800/40 text-[11px] font-bold px-2.5 py-0.5 rounded-full uppercase">
                {item.direction === 'MADE_BY_ME' ? 'OUTGOING COMMITMENT' : 'INCOMING COMMITMENT'}
              </span>

              {/* Pending Review Chip */}
              <span className="bg-white dark:bg-black text-black dark:text-white border border-black/20 dark:border-white/20 text-[11px] font-bold px-2.5 py-0.5 rounded-full uppercase">
                {item.staged ? 'STAGED' : 'PENDING REVIEW'}
              </span>

              {/* Ambiguity Guard Warning Chip */}
              {item.is_ambiguous && (
                <span className="bg-[#FEF3C7] dark:bg-amber-950/40 text-[#D97706] dark:text-[#FBBF24] border border-[#FDE68A] dark:border-amber-800/40 text-[11px] font-bold px-2.5 py-0.5 rounded-full uppercase">
                  Ambiguity Guard ({Math.round((item.confidence_score || 0.68) * 100)}% Conf)
                </span>
              )}

              {/* Due Soon Chip */}
              <span className="bg-[#FEF3C7] dark:bg-amber-950/40 text-[#D97706] dark:text-[#FBBF24] border border-[#FDE68A] dark:border-amber-800/40 text-[11px] font-bold px-2.5 py-0.5 rounded-full uppercase">
                {isFirst ? 'DUE SOON (19H)' : item.verbal_deadline.toUpperCase()}
              </span>

              {isFirst && (
                <span className="bg-[#EFF6FF] dark:bg-blue-950/40 text-[#2563EB] dark:text-[#93C5FD] border border-[#DBEAFE] dark:border-blue-800/40 text-[11px] font-bold px-2.5 py-0.5 rounded-full uppercase">
                  ACTIVE FOCUS
                </span>
              )}
            </div>

            {/* Right Due Text */}
            <div className="text-[12.5px] text-[#52525B] dark:text-[#A1A1AA]">
              Due: <strong className="text-black dark:text-white font-bold">{item.verbal_deadline}</strong>
            </div>
          </div>

          {/* Task Title & Description */}
          <h3 className="text-[19px] font-bold text-black dark:text-white tracking-tight mb-1">
            {item.task_title}
          </h3>
          <p className="text-[13.5px] text-[#52525B] dark:text-[#A1A1AA] leading-relaxed mb-3">
            {item.summary}
          </p>

          {/* Spoken Quote Callout Box */}
          {item.quote && (
            <div className="mb-3.5 p-3 bg-white dark:bg-black border border-[#E5E7EB] dark:border-[#27272A] rounded-lg text-[12.5px] leading-relaxed text-black/80 dark:text-white/80 font-mono">
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1">
                  <span className="text-[#52525B] dark:text-[#A1A1AA] select-none mr-1.5">&ldquo;</span>
                  <span>{item.quote}</span>
                  <span className="text-[#52525B] dark:text-[#A1A1AA] select-none ml-1.5">&rdquo;</span>
                  {item.captured_at && (
                    <span className="block mt-1 text-[11px] text-[#52525B] dark:text-[#A1A1AA] font-sans">
                      Captured via Bee Wearable · {item.captured_at}
                    </span>
                  )}
                </div>
                <button
                  type="button"
                  onClick={handlePlayAudio}
                  className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-sans font-medium transition-all cursor-pointer shadow-2xs shrink-0 ${
                    isPlayingAudio
                      ? 'bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-400 dark:border-emerald-600 text-emerald-800 dark:text-emerald-300'
                      : 'bg-white dark:bg-black border border-black/15 dark:border-white/20 text-black dark:text-white hover:border-black dark:hover:border-white'
                  }`}
                  title={isPlayingAudio ? 'Click to stop audio' : 'Listen to captured wearable audio'}
                >
                  {isPlayingAudio ? (
                    <>
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                      <span className="font-mono font-bold">Stop Audio</span>
                    </>
                  ) : (
                    <>
                      <span className="text-[10px]">▶</span>
                      <span>Play Audio ({item.audio_duration_seconds || 8}s)</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          )}

          {/* Counterparty & Metadata Line */}
          <div className="text-[13px] text-[#52525B] dark:text-[#A1A1AA] mb-4 flex items-center gap-2 flex-wrap">
            <span>Counterparty: <strong className="text-black dark:text-white font-semibold">{item.counterparty_name}</strong></span>
            <span>·</span>
            <span>
              Email:{' '}
              <code className="text-blue-600 dark:text-sky-400 bg-[#E0F2FE] dark:bg-sky-950/40 px-2 py-0.5 rounded text-[12px] border border-[#BAE6FD] dark:border-sky-800/40 font-mono">
                {item.counterparty_email}
              </code>
            </span>
            <span>·</span>
            <span>
              ISO:{' '}
              <code className="text-black dark:text-white bg-white dark:bg-black px-2 py-0.5 rounded text-[12px] border border-[#E5E7EB] dark:border-[#27272A] font-mono tabular-nums">
                {item.iso_deadline}
              </code>
            </span>
          </div>

          {/* Staging Tabs (Todoist Task, Gmail Draft, Calendar Event) */}
          <div className="border-b border-[#E5E7EB] dark:border-[#27272A] mb-4">
            <div className="flex items-center gap-6">
              <button
                onClick={() => setActiveTab('todoist')}
                className={`flex items-center gap-2 pb-2 text-[13.5px] font-medium transition-colors border-b-2 cursor-pointer ${
                  activeTab === 'todoist'
                    ? 'border-black dark:border-white text-black dark:text-white font-semibold'
                    : 'border-transparent text-[#52525B] dark:text-[#A1A1AA] hover:text-black dark:hover:text-white'
                }`}
              >
                <TodoistIcon className="w-4 h-4 shrink-0" />
                <span>Todoist Task</span>
              </button>

              <button
                onClick={() => setActiveTab('gmail')}
                className={`flex items-center gap-2 pb-2 text-[13.5px] font-medium transition-colors border-b-2 cursor-pointer ${
                  activeTab === 'gmail'
                    ? 'border-black dark:border-white text-black dark:text-white font-semibold'
                    : 'border-transparent text-[#52525B] dark:text-[#A1A1AA] hover:text-black dark:hover:text-white'
                }`}
              >
                <GmailIcon className="w-4 h-4 shrink-0" />
                <span>Gmail Draft</span>
              </button>

              <button
                onClick={() => setActiveTab('calendar')}
                className={`flex items-center gap-2 pb-2 text-[13.5px] font-medium transition-colors border-b-2 cursor-pointer ${
                  activeTab === 'calendar'
                    ? 'border-black dark:border-white text-black dark:text-white font-semibold'
                    : 'border-transparent text-[#52525B] dark:text-[#A1A1AA] hover:text-black dark:hover:text-white'
                }`}
              >
                <CalendarIcon className="w-4 h-4 shrink-0" />
                <span>Calendar Event</span>
              </button>
            </div>
          </div>

          {/* Tab Panels */}
          {activeTab === 'todoist' && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
              <div className="md:col-span-3">
                <label className="block text-[12px] font-medium text-[#52525B] dark:text-[#A1A1AA] mb-1.5">
                  Task Title
                </label>
                <input
                  type="text"
                  value={item.task_title}
                  onChange={(e) => handleTitleChange(e.target.value)}
                  className="w-full h-[40px] bg-white dark:bg-black border border-black dark:border-[#3F3F46] rounded-lg px-3.5 text-[13.5px] text-black dark:text-white focus:outline-none focus:ring-1 focus:ring-blue-500 shadow-xs transition-colors"
                />
              </div>
              <div>
                <label className="block text-[12px] font-medium text-[#52525B] dark:text-[#A1A1AA] mb-1.5">
                  Priority Level
                </label>
                <div className="relative flex items-center">
                  <select
                    value={item.priority}
                    onChange={(e) => handlePriorityChange(e.target.value)}
                    className="w-full h-[40px] bg-white dark:bg-black border border-black dark:border-[#3F3F46] rounded-lg px-3.5 pr-11 text-[13px] text-black dark:text-white appearance-none focus:outline-none shadow-xs cursor-pointer font-medium"
                  >
                    <option value="P1 - High" className="bg-white dark:bg-black text-black dark:text-white">P1 - High</option>
                    <option value="P2 - Medium" className="bg-white dark:bg-black text-black dark:text-white">P2 - Medium</option>
                    <option value="P3 - Low" className="bg-white dark:bg-black text-black dark:text-white">P3 - Low</option>
                  </select>
                  <div className="pointer-events-none absolute right-1.5 inset-y-0 my-auto w-7 h-7 bg-black dark:bg-white text-white dark:text-black rounded-md flex items-center justify-center shadow-xs">
                    <ChevronDownIcon className="w-3.5 h-3.5 text-white dark:text-black" strokeWidth={2.5} />
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'gmail' && (
            <div className="flex flex-col gap-3 mb-4">
              <div>
                <label className="block text-[12px] font-medium text-[#52525B] dark:text-[#A1A1AA] mb-1.5">
                  Subject
                </label>
                <input
                  type="text"
                  value={item.email_subject || `Follow up: ${item.task_title}`}
                  onChange={(e) => handleSubjectChange(e.target.value)}
                  className="w-full h-[40px] bg-white dark:bg-black border border-black dark:border-[#3F3F46] rounded-lg px-3.5 text-[13.5px] text-black dark:text-white focus:outline-none focus:ring-1 focus:ring-blue-500 shadow-xs transition-colors"
                />
              </div>
              <div>
                <label className="block text-[12px] font-medium text-[#52525B] dark:text-[#A1A1AA] mb-1.5">
                  Email Draft Body (Drafts only — strictly enforced via gmail.compose scope)
                </label>
                <textarea
                  value={
                    item.email_body ||
                    `Hi ${item.counterparty_name},\n\nJust following up on our sync. I'll send over the revised pitch deck with updated benchmarks by 5 PM tomorrow.\n\nBest,\nMe`
                  }
                  onChange={(e) => handleBodyChange(e.target.value)}
                  rows={3}
                  className="w-full bg-white dark:bg-black border border-black dark:border-[#3F3F46] rounded-lg p-3.5 text-[13.5px] text-black dark:text-white focus:outline-none focus:ring-1 focus:ring-blue-500 shadow-xs transition-colors"
                />
              </div>
            </div>
          )}

          {activeTab === 'calendar' && (
            <div className="flex flex-col gap-3 mb-4">
              <div>
                <label className="block text-[12px] font-medium text-[#52525B] dark:text-[#A1A1AA] mb-1.5">
                  Event Title
                </label>
                <input
                  type="text"
                  value={item.calendar_title || `Focus Session: ${item.task_title}`}
                  onChange={(e) => handleCalTitleChange(e.target.value)}
                  className="w-full h-[40px] bg-white dark:bg-black border border-black dark:border-[#3F3F46] rounded-lg px-3.5 text-[13.5px] text-black dark:text-white focus:outline-none focus:ring-1 focus:ring-blue-500 shadow-xs transition-colors"
                />
              </div>
              <div className="text-[12.5px] text-[#52525B] dark:text-[#A1A1AA] flex items-center gap-1.5 font-mono">
                <span>Duration: {item.calendar_duration || 30} min · Tentative time-block on Google Calendar</span>
              </div>
            </div>
          )}

          {/* Action Buttons: Approve & Stage Action vs Dismiss */}
          <div className="flex items-center gap-3 mt-4">
            <button
              onClick={() => onStage(item.id)}
              disabled={item.staged}
              className={`h-[36px] px-5 rounded-lg text-[13px] font-medium transition-all shadow-xs flex items-center justify-center gap-2 cursor-pointer ${
                item.staged
                  ? 'bg-white dark:bg-black border border-black/15 dark:border-white/15 text-black/40 dark:text-white/40 cursor-not-allowed'
                  : 'bg-black dark:bg-white text-white dark:text-black font-semibold hover:opacity-90 active:scale-98'
              }`}
            >
              {item.staged ? 'Staged to Destinations' : 'Approve & Stage Action'}
            </button>

            <button
              onClick={() => onDismiss(item.id)}
              className="h-[36px] px-4 rounded-lg text-[13px] font-medium text-black dark:text-white bg-white dark:bg-black border border-black/20 dark:border-[#27272A] hover:border-black dark:hover:border-white hover:bg-black hover:text-white dark:hover:bg-white dark:hover:text-black transition-all shadow-xs cursor-pointer active:scale-98"
            >
              Dismiss
            </button>
          </div>

          {/* Staged Safely Confirmation Banner */}
          {item.staged && (
            <div className="mt-3.5 p-3.5 bg-white dark:bg-black border border-emerald-500 rounded-lg text-[13px] text-emerald-700 dark:text-emerald-400 flex items-center gap-2">
              <CheckIcon className="w-4 h-4 text-emerald-600 dark:text-emerald-400 shrink-0" />
              <span>
                <strong className="font-semibold">Staged safely (200 OK):</strong>{' '}
                Created Gmail draft (never auto-sent via gmail.compose), created Todoist task with #promise-keeper tag, and scheduled tentative calendar event.{' '}
                <a
                  href="https://mail.google.com/mail/u/0/#drafts"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-emerald-700 dark:text-emerald-300 font-semibold underline ml-1"
                >
                  View Draft ↗
                </a>
              </span>
            </div>
          )}
        </div>
      )}
    </article>
  );
};
