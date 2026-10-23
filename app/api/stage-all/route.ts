import { NextRequest, NextResponse } from 'next/server';
import { stageCommitmentAtomically } from '@/lib/dispatcher';
import { CommitmentItem } from '@/lib/types';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { items } = body as { items: CommitmentItem[] };

    if (!Array.isArray(items)) {
      return NextResponse.json(
        { success: false, message: 'Invalid items array.' },
        { status: 400 }
      );
    }

    const results = [];
    for (const item of items) {
      if (!item.staged) {
        const res = await stageCommitmentAtomically(item);
        results.push({ id: item.id, ...res });
      }
    }

    return NextResponse.json({
      success: true,
      stagedCount: results.filter((r) => r.success).length,
      results,
      items,
    });
  } catch (error: unknown) {
    return NextResponse.json(
      {
        success: false,
        message: error instanceof Error ? error.message : 'Stage all failed.',
      },
      { status: 500 }
    );
  }
}
