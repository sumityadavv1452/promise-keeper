'use client';

import React from 'react';
import { WaveformIcon, PulseDot } from './icons';

interface LiveStreamViewProps {
  onBackToCommitments: () => void;
}

export const LiveStreamView: React.FC<LiveStreamViewProps> = ({ onBackToCommitments }) => {
  const events = [
    {
      time: '09:41:04',
      speaker: 'Device Telemetry',
      isSystem: true,
      text: 'Bee Audio Stream connected via BLE · Diarization Active · 16kHz Sampling · Bedrock Nova Pro Engine Ready',
      extracted: null,
    },
    {
      time: '09:41:12',
      speaker: 'Speaker 1 (Me)',
      isSystem: false,
      isMe: true,
      text: "Hey Alex, thanks for the sync. I'll send you the revised pitch deck by 5 PM tomorrow with the updated architecture diagram.",
      extracted: {
        type: 'OUTGOING COMMITMENT',
        task: 'Send revised pitch deck to Alex',
        deadline: 'Tomorrow, 5:00 PM',
        confidence: '98.2%',
        status: 'Staged to Apps',
      },
    },
    {
      time: '09:41:20',
      speaker: 'Speaker 2 (Alex Rivera)',
      isSystem: false,
      isMe: false,
      text: "Sounds great. Make sure to review the Q3 analytics report before Wednesday noon so we're aligned for the client sync.",
      extracted: {
        type: 'INCOMING COMMITMENT',
        task: 'Review Q3 analytics report from Alex',
        deadline: 'Wednesday, 12:00 PM',
        confidence: '96.5%',
        status: 'Pending Review',
      },
    },
    {
      time: '09:41:28',
      speaker: 'Speaker 1 (Me)',
      isSystem: false,
      isMe: true,
      text: "Will do, let's also block 30 minutes on Thursday morning for a dry run.",
      extracted: null,
    },
    {
      time: '09:41:35',
      speaker: 'Speaker 2 (Alex Rivera)',
      isSystem: false,
      isMe: false,
      text: 'Perfect, calendar invite received. Looking forward to it.',
      extracted: null,
    },
  ];

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between gap-4 flex-wrap pb-3 border-b border-subtle">
        <button
          onClick={onBackToCommitments}
          className="h-[34px] px-3.5 bg-black dark:bg-white text-white dark:text-black text-[12.5px] font-semibold rounded-lg hover:opacity-90 active:scale-[0.98] transition-all shadow-xs cursor-pointer inline-flex items-center gap-1.5"
        >
          <span>← Back to Commitments</span>
        </button>

        <div className="text-[12px] text-muted flex items-center gap-2">
          <WaveformIcon className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
          <span>
            Hardware Source: <strong className="text-main font-semibold">Bee Wearable (BLE)</strong>
          </span>
          <span>·</span>
          <span className="inline-flex items-center gap-1 text-emerald-600 dark:text-emerald-400 font-medium">
            <PulseDot />
            <span>16kHz Active</span>
          </span>
        </div>
      </div>

      <div className="flex flex-col gap-3">
        {events.map((ev, i) => (
          <div
            key={i}
            className="p-4 rounded-xl border border-[#E5E7EB] dark:border-[#27272A] bg-white dark:bg-black text-[13px] shadow-xs transition-colors"
          >
            <div className="flex items-center gap-2 mb-1.5">
              <span className="font-mono text-[11px] text-muted tabular-nums">[{ev.time}]</span>
              <span
                className={`text-[12px] font-bold ${
                  ev.isSystem
                    ? 'text-muted'
                    : ev.isMe
                    ? 'text-blue-600 dark:text-sky-400'
                    : 'text-emerald-600 dark:text-emerald-400'
                }`}
              >
                {ev.speaker}:
              </span>
            </div>

            <p className="text-main leading-relaxed pl-1">{ev.text}</p>

            {ev.extracted && (
              <div className="mt-3 p-3 bg-white dark:bg-black border border-blue-400/40 dark:border-blue-500/30 rounded-lg flex items-center justify-between flex-wrap gap-2">
                <div className="flex items-center gap-2">
                  <span className="text-[10.5px] font-bold uppercase tracking-wider bg-blue-100 dark:bg-blue-950/60 text-blue-700 dark:text-sky-300 px-2 py-0.5 rounded">
                    {ev.extracted.type}
                  </span>
                  <span className="font-semibold text-main text-[13px]">
                    {ev.extracted.task}
                  </span>
                </div>
                <div className="text-[12px] text-muted flex items-center gap-2 font-mono">
                  <span>Due: {ev.extracted.deadline}</span>
                  <span className="text-emerald-600 dark:text-emerald-400 font-semibold tabular-nums">({ev.extracted.confidence})</span>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
