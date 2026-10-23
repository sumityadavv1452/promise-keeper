export interface CommitmentItem {
  id: string;
  task_title: string;
  summary: string;
  direction: 'MADE_BY_ME' | 'MADE_TO_ME' | 'RECEIVED_BY_ME';
  counterparty_name: string;
  counterparty_email: string;
  verbal_deadline: string;
  iso_deadline: string;
  priority: string;
  email_subject?: string;
  email_body?: string;
  calendar_title?: string;
  calendar_duration?: number;
  staged: boolean;
  staged_at?: string | null;
  is_ambiguous?: boolean;
  confidence_score?: number;
  quote?: string;
  captured_at?: string;
  enabled_destinations?: {
    gmail: boolean;
    calendar: boolean;
    todoist: boolean;
  };
  recommended_time_slot?: string;
  audio_duration_seconds?: number;
}

export interface TelemetryData {
  latencyMs: number;
  tokensUsed: number;
  estimatedCost: number;
  selectedModel: string;
  modelName: string;
}

export interface DaemonStatus {
  status: 'connected' | 'standby' | 'offline';
  batteryPercentage: number;
  diarization: string;
  ingestionMode: string;
  cliBridge: string;
}

export interface StagingResponse {
  success: boolean;
  message: string;
  services?: {
    todoist: { success: boolean; mode: string; taskId?: string };
    gmail: { success: boolean; mode: string; draftId?: string; url?: string };
    calendar: { success: boolean; mode: string; eventId?: string; htmlLink?: string };
  };
}
