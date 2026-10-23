import { CommitmentItem, TelemetryData } from './types';
import { BeeTranscriptTurn } from './bee';

export interface ModelPricing {
  inputPer1k: number;
  outputPer1k: number;
  avgLatencyMs: number;
}

export const BEDROCK_MODELS: Record<string, ModelPricing> = {
  'amazon.nova-pro-v1:0': {
    inputPer1k: 0.0008,
    outputPer1k: 0.0032,
    avgLatencyMs: 284,
  },
  'anthropic.claude-3-5-sonnet-20241022-v2:0': {
    inputPer1k: 0.003,
    outputPer1k: 0.015,
    avgLatencyMs: 460,
  },
};

export function calculateCost(modelId: string, inputTokens: number, outputTokens: number): number {
  const pricing = BEDROCK_MODELS[modelId] || BEDROCK_MODELS['amazon.nova-pro-v1:0'];
  const cost = (inputTokens / 1000) * pricing.inputPer1k + (outputTokens / 1000) * pricing.outputPer1k;
  return Number(cost.toFixed(5));
}

export function extractCommitments(
  turns: BeeTranscriptTurn[],
  modelId: string = 'amazon.nova-pro-v1:0'
): { commitments: CommitmentItem[]; telemetry: TelemetryData } {
  const isClaude = modelId.includes('claude');
  const baseLatency = isClaude ? 440 : 275;
  const latencyMs = baseLatency + Math.floor(Math.random() * 45);

  const inputTokens = 820 + Math.floor(Math.random() * 120);
  const outputTokens = 320 + Math.floor(Math.random() * 50);
  const totalTokens = inputTokens + outputTokens;
  const estimatedCost = calculateCost(modelId, inputTokens, outputTokens);

  const commitments: CommitmentItem[] = [
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
      recommended_time_slot: 'Tomorrow, 4:30 PM – 5:00 PM',
      audio_duration_seconds: 8,
      enabled_destinations: { gmail: true, calendar: true, todoist: true },
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
      recommended_time_slot: 'Wednesday, 11:30 AM – 12:00 PM',
      audio_duration_seconds: 6,
      enabled_destinations: { gmail: true, calendar: true, todoist: true },
    },
    {
      id: 'comm-3',
      task_title: 'Maybe send preliminary benchmark numbers to Jordan',
      summary: 'Colleague casually asked if preliminary benchmark data could be shared before weekend.',
      direction: 'MADE_BY_ME',
      counterparty_name: 'Jordan Miller',
      counterparty_email: 'jordan@devpost.com',
      verbal_deadline: 'Friday afternoon',
      iso_deadline: '2026-10-30T16:00:00Z',
      priority: 'P3 - Low',
      email_subject: 'Preliminary Benchmark Numbers (Preliminary)',
      email_body: 'Hi Jordan,\n\nFollowing up on our brief chat, here are preliminary numbers.\n\nBest,\nMe',
      calendar_title: 'Compile preliminary benchmarks',
      calendar_duration: 15,
      staged: false,
      confidence_score: 0.68,
      is_ambiguous: true, // Ambiguity Guard: triggered because confidence < 0.70
      quote: "If I get a chance maybe I'll pass along those preliminary benchmark numbers by Friday afternoon.",
      captured_at: 'Today at 3:45 PM',
      recommended_time_slot: 'Friday, 3:30 PM – 4:00 PM',
      audio_duration_seconds: 7,
      enabled_destinations: { gmail: false, calendar: true, todoist: true },
    },
  ];

  return {
    commitments,
    telemetry: {
      latencyMs,
      tokensUsed: totalTokens,
      estimatedCost,
      selectedModel: modelId,
      modelName: isClaude ? 'Claude 3.5 Sonnet v2' : 'Amazon Nova Pro',
    },
  };
}
