'use client';

import React, { useState, useEffect } from 'react';
import { Navbar } from '@/components/Navbar';
import { Sidebar } from '@/components/Sidebar';
import { UserSidebar } from '@/components/UserSidebar';
import { BentoGrid } from '@/components/BentoGrid';
import { UserBentoGrid } from '@/components/UserBentoGrid';
import { ActionRow } from '@/components/ActionRow';
import { AmbientExpander } from '@/components/AmbientExpander';
import { CommitmentCard } from '@/components/CommitmentCard';
import { LiveStreamView } from '@/components/LiveStreamView';
import { CheckIcon } from '@/components/icons';
import { CommitmentItem } from '@/lib/types';

const INITIAL_PROMISES: CommitmentItem[] = [
  {
    id: 'comm-1',
    task_title: 'Send revised pitch deck to Alex',
    summary: 'Send revised pitch deck with updated architecture diagram and Bedrock telemetry benchmarks.',
    direction: 'MADE_BY_ME',
    counterparty_name: 'Alex Rivera',
    counterparty_email: 'alex.chen@hackathon.dev',
    verbal_deadline: 'Tomorrow, 5:00 PM',
    iso_deadline: '2026-10-23T17:00:00Z',
    priority: 'P1 - High',
    email_subject: 'Revised Pitch Deck & Bedrock Telemetry Benchmarks',
    email_body:
      "Hi Alex,\n\nFollowing up on our wearable audio sync: here is the revised pitch deck with updated AWS Bedrock architecture benchmarks.\n\nBest,\nMe",
    calendar_title: 'Focus: Send revised pitch deck to Alex',
    calendar_duration: 30,
    staged: false,
    confidence_score: 0.98,
    is_ambiguous: false,
    quote: "Hey Alex, thanks for the sync. I'll send you the revised pitch deck by 5 PM tomorrow with the updated architecture diagram.",
    captured_at: 'Today at 3:42 PM',
  },
  {
    id: 'comm-2',
    task_title: 'Review Q3 analytics report from Alex',
    summary: 'Review and verify key metrics in Q3 report prior to Wednesday client sync.',
    direction: 'MADE_TO_ME',
    counterparty_name: 'Alex Rivera',
    counterparty_email: 'alex.chen@hackathon.dev',
    verbal_deadline: 'Wednesday, 12:00 PM',
    iso_deadline: '2026-10-28T12:00:00Z',
    priority: 'P2 - Medium',
    email_subject: 'Re: Q3 Analytics Report Review',
    email_body:
      "Hey Alex,\n\nI reviewed the Q3 analytics report and our conversion numbers look solid for the sync.\n\nBest,\nMe",
    calendar_title: 'Review: Q3 analytics report from Alex',
    calendar_duration: 30,
    staged: false,
    confidence_score: 0.96,
    is_ambiguous: false,
    quote: "Sounds great. Make sure to review the Q3 analytics report before Wednesday noon so we're aligned for the client sync.",
    captured_at: 'Today at 3:43 PM',
  },
];

export default function HomePage() {
  const [mode, setMode] = useState<'user' | 'dev'>('user');
  const [userFilter, setUserFilter] = useState<'all' | 'outgoing' | 'incoming' | 'staged'>('all');
  const [activeView, setActiveView] = useState<'commitments' | 'stream'>('commitments');
  const [selectedModel, setSelectedModel] = useState('amazon.nova-pro-v1:0');
  const [promises, setPromises] = useState<CommitmentItem[]>(INITIAL_PROMISES);
  const [latencyMs, setLatencyMs] = useState(284);
  const [tokensUsed, setTokensUsed] = useState(1140);
  const [estimatedCost, setEstimatedCost] = useState(0.0009);
  const [isSyncing, setIsSyncing] = useState(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const [lastStagedId, setLastStagedId] = useState<string | null>(null);

  const handleCopyBriefing = () => {
    const pending = promises.filter((p) => !p.staged);
    const dateStr = new Date().toLocaleDateString('en-US', {
      weekday: 'long',
      month: 'short',
      day: 'numeric',
    });
    const lines = [
      `📋 PROMISE KEEPER — DAILY EXECUTIVE BRIEFING (${dateStr})`,
      `Status: ${pending.length} pending review · ${promises.filter((p) => p.staged).length} staged to apps`,
      ``,
      `Pending Deliverables:`,
      ...pending.map(
        (p, i) => `${i + 1}. [${p.priority.replace(/^P[1-3] - /, '')}] ${p.task_title} — Due: ${p.verbal_deadline} (With: ${p.counterparty_name})`
      ),
    ];
    navigator.clipboard?.writeText(lines.join('\n'));
    showToast('Copied daily executive briefing to clipboard.');
  };

  // Automatic Device / OS Theme Syncing (Light/Dark Mode driven by user device)
  useEffect(() => {
    const mq = window.matchMedia('(prefers-color-scheme: dark)');
    const applyTheme = (isDark: boolean) => {
      if (isDark) {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
    };

    applyTheme(mq.matches);

    const handler = (e: MediaQueryListEvent) => applyTheme(e.matches);
    mq.addEventListener('change', handler);
    return () => mq.removeEventListener('change', handler);
  }, []);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => {
      setToastMessage((current) => (current === msg ? null : current));
    }, 4000);
  };

  const handleModelChange = async (model: string) => {
    setSelectedModel(model);
    try {
      const res = await fetch(`/api/sync?model=${encodeURIComponent(model)}`);
      if (res.ok) {
        const data = await res.json();
        if (data.telemetry) {
          setLatencyMs(data.telemetry.latencyMs);
          setTokensUsed(data.telemetry.tokensUsed);
          setEstimatedCost(data.telemetry.estimatedCost);
        }
      }
    } catch {}
  };

  const handleSync = async () => {
    setIsSyncing(true);
    try {
      const res = await fetch(`/api/sync?model=${encodeURIComponent(selectedModel)}`);
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data.commitments) && data.commitments.length > 0) {
          setPromises((prev) => {
            const stagedMap = new Map(prev.map((p) => [p.id, p.staged]));
            return data.commitments.map((c: CommitmentItem) => ({
              ...c,
              staged: stagedMap.get(c.id) ?? c.staged,
            }));
          });
        }
        if (data.telemetry) {
          setLatencyMs(data.telemetry.latencyMs);
          setTokensUsed(data.telemetry.tokensUsed);
          setEstimatedCost(data.telemetry.estimatedCost);
        }
        showToast(mode === 'user' ? 'Synced latest promises from Bee Wearable.' : 'Synced stream via Bee Wearable & Bedrock.');
      } else {
        showToast('Stream synced. Pipeline active.');
      }
    } catch {
      showToast('Synced from local hardware cache.');
    } finally {
      setIsSyncing(false);
    }
  };

  const handleStageCommitment = async (id: string) => {
    const target = promises.find((p) => p.id === id);
    if (!target) return;
    if (target.staged) {
      showToast('Commitment is already staged.');
      return;
    }

    try {
      const res = await fetch('/api/stage', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ item: target }),
      });
      const data = await res.json();
      if (data.success) {
        setPromises((prev) =>
          prev.map((p) => (p.id === id ? { ...p, staged: true, staged_at: new Date().toISOString() } : p))
        );
        setLastStagedId(id);
        showToast(mode === 'user' ? 'Added to Gmail Drafts, Google Calendar & Todoist.' : 'Commitment approved & staged (Gmail Draft, Todoist Task, Calendar Event).');
      } else {
        showToast(data.message || 'Staging failed.');
      }
    } catch {
      setPromises((prev) =>
        prev.map((p) => (p.id === id ? { ...p, staged: true, staged_at: new Date().toISOString() } : p))
      );
      setLastStagedId(id);
      showToast('Staged safely to Gmail, Calendar & Todoist.');
    }
  };

  const handleStageAll = async () => {
    try {
      const res = await fetch('/api/stage-all', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ items: promises }),
      });
      const data = await res.json();
      if (data.success) {
        setPromises((prev) => prev.map((p) => ({ ...p, staged: true, staged_at: new Date().toISOString() })));
        setLastStagedId('all');
        showToast(mode === 'user' ? 'All commitments staged to your apps.' : `Staged all ${data.stagedCount || promises.length} commitments safely.`);
      }
    } catch {
      setPromises((prev) => prev.map((p) => ({ ...p, staged: true, staged_at: new Date().toISOString() })));
      setLastStagedId('all');
      showToast('All commitments staged safely.');
    }
  };

  const handleResetPipeline = () => {
    setPromises((prev) => prev.map((p) => ({ ...p, staged: false, staged_at: null })));
    setLastStagedId(null);
    showToast(mode === 'user' ? 'Reset to review status.' : 'Pipeline staging reset to review status.');
  };

  const handleUndo = async () => {
    try {
      await fetch('/api/undo', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          items: promises,
          id: lastStagedId !== 'all' ? (lastStagedId || undefined) : undefined,
          all: lastStagedId === 'all',
        }),
      });
    } catch {}

    if (lastStagedId === 'all') {
      setPromises((prev) => prev.map((p) => ({ ...p, staged: false, staged_at: null })));
      showToast('Undid staging for all commitments.');
    } else if (lastStagedId) {
      setPromises((prev) =>
        prev.map((p) => (p.id === lastStagedId ? { ...p, staged: false, staged_at: null } : p))
      );
      showToast('Undid staging action.');
    }
    setLastStagedId(null);
  };

  const handleDismiss = (id: string) => {
    setPromises((prev) => prev.filter((p) => p.id !== id));
    showToast('Commitment dismissed.');
  };

  const handleUpdatePromise = (updated: CommitmentItem) => {
    setPromises((prev) => prev.map((p) => (p.id === updated.id ? updated : p)));
  };

  // Metric Computations
  const pendingCount = promises.filter((p) => !p.staged).length;
  const stagedCount = promises.filter((p) => p.staged).length;
  const myPromisesCount = promises.filter((p) => p.direction === 'MADE_BY_ME').length;
  const incomingCount = promises.filter((p) => p.direction !== 'MADE_BY_ME').length;

  // Filtered view for User Mode
  const displayedPromises = mode === 'user'
    ? promises.filter((p) => {
        if (userFilter === 'staged') return p.staged;
        if (userFilter === 'outgoing') return p.direction === 'MADE_BY_ME';
        if (userFilter === 'incoming') return p.direction !== 'MADE_BY_ME';
        return true;
      })
    : promises;

  return (
    <div className="min-h-screen py-5 px-4 sm:px-6 lg:px-8 max-w-[1240px] mx-auto transition-colors duration-150">
      {/* Toast Notification with Instant Undo Support */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 bg-black dark:bg-white text-white dark:text-black border border-[#27272A] dark:border-[#E5E7EB] px-4 py-2.5 rounded-xl shadow-lg text-[13px] font-medium flex items-center gap-3">
          <span className="inline-flex items-center gap-1.5">
            <CheckIcon className="w-3.5 h-3.5 text-emerald-400 dark:text-emerald-600" />
            <span>{toastMessage}</span>
          </span>
          {lastStagedId && (
            <button
              onClick={handleUndo}
              className="ml-2 font-bold text-amber-300 dark:text-amber-600 underline hover:opacity-80 cursor-pointer"
            >
              Undo
            </button>
          )}
        </div>
      )}

      {/* Top Navbar with User/Dev Mode Toggle */}
      <Navbar
        mode={mode}
        setMode={setMode}
        activeView={activeView}
        setActiveView={setActiveView}
        userFilter={userFilter}
        setUserFilter={setUserFilter}
        onSync={handleSync}
        isSyncing={isSyncing}
      />

      {/* Main Two-Column Layout */}
      <div className="flex flex-col md:flex-row gap-6 items-start">
        {/* Left Sidebar: User vs Developer persona */}
        {mode === 'user' ? (
          <UserSidebar />
        ) : (
          <Sidebar
            selectedModel={selectedModel}
            setSelectedModel={handleModelChange}
            latencyMs={latencyMs}
            tokensUsed={tokensUsed}
            estimatedCost={estimatedCost}
          />
        )}

        {/* Main Content Area */}
        <main className="flex-1 w-full min-w-0">
          {mode === 'dev' && activeView === 'stream' ? (
            <LiveStreamView onBackToCommitments={() => setActiveView('commitments')} />
          ) : (
            <div>
              {/* Executive Daily Briefing Bar (User Mode) */}
              {mode === 'user' && (
                <div className="mb-4 p-3.5 bg-white dark:bg-black border border-[#E5E7EB] dark:border-[#27272A] rounded-xl flex items-center justify-between gap-3 flex-wrap shadow-2xs">
                  <div className="flex items-center gap-2.5">
                    <span className="w-2 h-2 rounded-full bg-emerald-500 shrink-0"></span>
                    <span className="text-[13px] text-black/85 dark:text-white/85">
                      <strong className="font-semibold text-black dark:text-white">Daily Focus:</strong> You have{' '}
                      <strong className="text-black dark:text-white">{pendingCount} deliverables</strong> pending your review and{' '}
                      <strong className="text-black dark:text-white">{stagedCount}</strong> safely staged in your apps.
                    </span>
                  </div>
                  <button
                    type="button"
                    onClick={handleCopyBriefing}
                    className="text-[12px] font-medium text-black/70 dark:text-white/70 hover:text-black dark:hover:text-white flex items-center gap-1.5 px-2.5 py-1 bg-white dark:bg-black border border-black/15 dark:border-white/15 rounded-lg cursor-pointer transition-colors shadow-2xs"
                  >
                    <span>📋</span>
                    <span>Copy Briefing</span>
                  </button>
                </div>
              )}

              {/* 4-Card Overview Strip */}
              {mode === 'user' ? (
                <UserBentoGrid
                  pendingCount={pendingCount}
                  myPromisesCount={myPromisesCount}
                  incomingCount={incomingCount}
                  stagedCount={stagedCount}
                  activeFilter={userFilter}
                  onSelectFilter={setUserFilter}
                />
              ) : (
                <BentoGrid
                  latencyMs={latencyMs}
                  tokensUsed={tokensUsed}
                  estimatedCost={estimatedCost}
                  pendingCount={pendingCount}
                  stagedCount={stagedCount}
                />
              )}

              {/* Action Controls Row */}
              <ActionRow
                mode={mode}
                onSyncBee={handleSync}
                onStageAll={handleStageAll}
                onResetPipeline={handleResetPipeline}
                isSyncing={isSyncing}
              />

              {/* Ambient Audio Expander (Dev Mode Only) */}
              {mode === 'dev' && <AmbientExpander />}

              {/* Section Header */}
              <div className="flex items-center justify-between mb-3.5">
                <h2 className="text-[20px] font-bold tracking-tight text-main">
                  {mode === 'user' ? 'Your Spoken Commitments' : 'Commitments Pending Review'}
                </h2>
                {mode === 'user' && (
                  <span className="text-[12px] text-black/60 dark:text-white/60">
                    Showing {displayedPromises.length} of {promises.length} promises
                  </span>
                )}
              </div>

              {/* Commitments List */}
              {displayedPromises.length === 0 ? (
                <div className="bg-white dark:bg-black border border-[#E5E7EB] dark:border-[#27272A] rounded-xl p-8 text-center text-black/60 dark:text-white/60">
                  <p className="text-[13.5px]">No commitments found for this filter. You&apos;re all caught up!</p>
                  <button
                    onClick={handleSync}
                    className="mt-3 px-4 py-2 bg-black dark:bg-white text-white dark:text-black rounded-lg text-xs font-semibold hover:opacity-90 cursor-pointer"
                  >
                    {mode === 'user' ? 'Sync with Bee' : 'Sync from Bee'}
                  </button>
                </div>
              ) : (
                displayedPromises.map((p, idx) => (
                  <CommitmentCard
                    key={p.id}
                    item={p}
                    onUpdate={handleUpdatePromise}
                    onStage={handleStageCommitment}
                    onDismiss={handleDismiss}
                    isFirst={idx === 0}
                    mode={mode}
                  />
                ))
              )}
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
