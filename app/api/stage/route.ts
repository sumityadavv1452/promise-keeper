import { NextRequest, NextResponse } from 'next/server';
import { stageCommitmentAtomically } from '@/lib/dispatcher';
import { CommitmentItem } from '@/lib/types';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { item, userEdits } = body as {
      item: CommitmentItem;
      userEdits?: Partial<CommitmentItem>;
    };

    if (!item || !item.id) {
      return NextResponse.json(
        { success: false, message: 'Missing commitment item payload.' },
        { status: 400 }
      );
    }

    const result = await stageCommitmentAtomically(item, userEdits);

    if (!result.success && result.message === 'Commitment already staged.') {
      return NextResponse.json(result, { status: 409 });
    }

    return NextResponse.json({
      ...result,
      stagedItem: item,
    });
  } catch (error: unknown) {
    return NextResponse.json(
      {
        success: false,
        message: error instanceof Error ? error.message : 'Staging failed unexpectedly.',
      },
      { status: 500 }
    );
  }
}
