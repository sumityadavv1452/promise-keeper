import { NextRequest, NextResponse } from 'next/server';
import { fetchBeeTranscripts, checkBeeDaemonStatus } from '@/lib/bee';
import { extractCommitments } from '@/lib/bedrock';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const model = searchParams.get('model') || 'amazon.nova-pro-v1:0';

    // 1. Ingest wearable transcripts
    const transcripts = fetchBeeTranscripts();

    // 2. Extract commitments via Bedrock with telemetry
    const { commitments, telemetry } = extractCommitments(transcripts, model);

    // 3. Daemon status
    const daemon = checkBeeDaemonStatus();

    return NextResponse.json({
      success: true,
      commitments,
      telemetry,
      daemon,
      timestamp: new Date().toISOString(),
    });
  } catch (error: unknown) {
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to sync with Bee wearable stream',
      },
      { status: 500 }
    );
  }
}
