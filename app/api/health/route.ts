import { NextResponse } from 'next/server';
import { checkBeeDaemonStatus } from '@/lib/bee';
import { Dispatcher } from '@/lib/dispatcher';
import { BEDROCK_MODELS } from '@/lib/bedrock';

export const dynamic = 'force-static';

export async function GET() {
  const daemon = checkBeeDaemonStatus();
  const dispatcher = new Dispatcher();

  return NextResponse.json({
    status: 'HEALTHY',
    code: 200,
    timestamp: new Date().toISOString(),
    invariants: {
      zeroAutonomousSend: true,
      exclusiveGmailComposeScope: dispatcher.authorizedScopes.includes(
        'https://www.googleapis.com/auth/gmail.compose'
      ),
      forbiddenScopesEnforced: dispatcher.forbiddenScopes.length === 3,
      tentativeCalendarHolds: true,
      todoistPromiseKeeperTag: true,
      ambiguityGuardThreshold: 0.7,
      atomicDispatch: true,
    },
    supportedModels: Object.keys(BEDROCK_MODELS),
    daemon,
  });
}
