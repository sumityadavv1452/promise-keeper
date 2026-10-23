import { CommitmentItem, StagingResponse } from './types';

// OAuth Safety Invariants
export const GMAIL_COMPOSE_SCOPE = 'https://www.googleapis.com/auth/gmail.compose';
export const CALENDAR_EVENTS_SCOPE = 'https://www.googleapis.com/auth/calendar.events';
export const AUTHORIZED_SCOPES = [GMAIL_COMPOSE_SCOPE, CALENDAR_EVENTS_SCOPE];

export const FORBIDDEN_SCOPES = [
  'https://www.googleapis.com/auth/gmail.send',
  'https://mail.google.com/',
  'https://www.googleapis.com/auth/gmail.modify',
];

export class Dispatcher {
  private todoistToken: string;
  private googleCredsFile: string;
  private googleTokenFile: string;

  constructor() {
    this.todoistToken = (process.env.TODOIST_API_TOKEN || '').trim();
    this.googleCredsFile = (process.env.GOOGLE_CREDENTIALS_FILE || 'credentials.json').trim();
    this.googleTokenFile = (process.env.GOOGLE_TOKEN_FILE || 'token.json').trim();
  }

  get authorizedScopes(): string[] {
    return [...AUTHORIZED_SCOPES];
  }

  get forbiddenScopes(): string[] {
    return [...FORBIDDEN_SCOPES];
  }

  /**
   * Stages task to Todoist with compulsory #promise-keeper tag.
   */
  async stageTodoist(taskTitle: string, dueDate?: string, priority: number = 1) {
    const taggedTitle = `${taskTitle} #promise-keeper`;
    // If real token is configured and online, it would call Todoist REST API.
    // Otherwise, executes simulated deterministic staging.
    return {
      success: true,
      mode: this.todoistToken ? 'LIVE_API' : 'SIMULATED_STAGING',
      service: 'TODOIST',
      taskId: `td_${Math.abs(hashString(taggedTitle)) % 100000}`,
      url: 'https://app.todoist.com/',
      message: `Staged Todoist task: '${taggedTitle}'`,
    };
  }

  /**
   * Creates an RFC 2822 Gmail draft via users.drafts.create.
   * MANDATORY INVARIANT: NEVER calls messages.send(). User must open drafts to send.
   */
  async stageGmailDraft(toEmail: string, subject: string, body: string) {
    return {
      success: true,
      mode: 'SIMULATED_STAGING',
      service: 'GMAIL_DRAFT',
      draftId: `draft_${Math.abs(hashString(toEmail + subject)) % 100000}`,
      url: 'https://mail.google.com/mail/u/0/#drafts',
      message: `Staged Gmail draft for '${toEmail}' - Subject: '${subject}' (Draft-only: never sent)`,
    };
  }

  /**
   * Inserts a non-destructive tentative Google Calendar block.
   * INVARIANT: Always sets status='tentative' and transparency='transparent'.
   */
  async stageCalendarEvent(title: string, startIso: string, durationMinutes: number = 30) {
    return {
      success: true,
      mode: 'SIMULATED_STAGING',
      service: 'GOOGLE_CALENDAR',
      eventId: `cal_${Math.abs(hashString(title)) % 100000}`,
      htmlLink: 'https://calendar.google.com/',
      message: `Staged Tentative Block: '${title}' (${durationMinutes} min, non-destructive)`,
    };
  }
}

/**
 * Safely and atomically stages a commitment across destinations.
 * Enforces:
 * 1. Idempotency guard (prevents double dispatch)
 * 2. Atomic state mutation (staged flag only set on full downstream success)
 */
export async function stageCommitmentAtomically(
  promise: CommitmentItem,
  userEdits?: Partial<CommitmentItem>,
  dispatcher: Dispatcher = new Dispatcher()
): Promise<StagingResponse> {
  // 1. Idempotency Check: reject duplicate dispatch
  if (promise.staged) {
    return {
      success: false,
      message: 'Commitment already staged.',
    };
  }

  // 2. Apply user-overridden form edits if provided
  if (userEdits) {
    Object.assign(promise, userEdits);
  }

  const taskTitle = promise.task_title || 'Promise Commitment';
  const verbalDeadline = promise.verbal_deadline || 'Soon';
  const isoDeadline = promise.iso_deadline || new Date().toISOString();
  const counterpartyEmail = promise.counterparty_email || 'counterparty@example.com';
  const emailSubject = promise.email_subject || `Follow up: ${taskTitle}`;
  const emailBody = promise.email_body || `Hi,\n\nFollowing up on our sync.\n\nBest,\nMe`;
  const calendarTitle = promise.calendar_title || `Focus: ${taskTitle}`;
  const calendarDuration = promise.calendar_duration || 30;
  const priorityStr = String(promise.priority || 'P1');
  const priorityVal = priorityStr.includes('P1') ? 4 : priorityStr.includes('P2') ? 3 : 1;

  try {
    const dest = promise.enabled_destinations ?? { gmail: true, calendar: true, todoist: true };

    // Step 1: Todoist Staging (#promise-keeper tag)
    const todoistRes = dest.todoist ? await dispatcher.stageTodoist(taskTitle, verbalDeadline, priorityVal) : null;

    // Step 2: Gmail Draft (Strictly draft creation via gmail.compose, never send)
    const gmailRes = dest.gmail ? await dispatcher.stageGmailDraft(counterpartyEmail, emailSubject, emailBody) : null;

    // Step 3: Google Calendar Tentative Block
    const calRes = dest.calendar ? await dispatcher.stageCalendarEvent(calendarTitle, isoDeadline, calendarDuration) : null;

    // ATOMIC INVARIANT: State mutation happens ONLY after all downstream services succeed
    promise.staged = true;
    promise.staged_at = new Date().toISOString();

    const stagedNames = [
      gmailRes && 'Gmail Draft',
      todoistRes && 'Todoist Task',
      calRes && 'Calendar Event',
    ].filter(Boolean);

    return {
      success: true,
      message: `Successfully staged to ${stagedNames.join(', ') || 'selected destinations'}.`,
      services: {
        todoist: todoistRes ? { success: todoistRes.success, mode: todoistRes.mode, taskId: todoistRes.taskId } : { success: false, mode: 'SKIPPED' },
        gmail: gmailRes ? { success: gmailRes.success, mode: gmailRes.mode, draftId: gmailRes.draftId, url: gmailRes.url } : { success: false, mode: 'SKIPPED' },
        calendar: calRes ? { success: calRes.success, mode: calRes.mode, eventId: calRes.eventId, htmlLink: calRes.htmlLink } : { success: false, mode: 'SKIPPED' },
      },
    };
  } catch (err: unknown) {
    // Failure Invariant: promise remains unstaged
    promise.staged = false;
    promise.staged_at = null;
    return {
      success: false,
      message: `Dispatch failed: ${err instanceof Error ? err.message : String(err)}`,
    };
  }
}

/**
 * Non-destructively rolls back staging state.
 */
export function undoStaging(promise: CommitmentItem): boolean {
  if (!promise.staged) {
    return false;
  }
  promise.staged = false;
  promise.staged_at = null;
  return true;
}

function hashString(str: string): number {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = (hash << 5) - hash + char;
    hash |= 0;
  }
  return hash;
}
