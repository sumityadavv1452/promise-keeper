import { NextRequest, NextResponse } from 'next/server';
import { undoStaging } from '@/lib/dispatcher';
import { CommitmentItem } from '@/lib/types';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { items, id, all } = body as {
      items?: CommitmentItem[];
      id?: string;
      all?: boolean;
    };

    if (all && Array.isArray(items)) {
      items.forEach((item) => undoStaging(item));
      return NextResponse.json({
        success: true,
        message: 'Undid staging for all commitments.',
        items,
      });
    }

    if (id && Array.isArray(items)) {
      const target = items.find((i) => i.id === id);
      if (target) {
        undoStaging(target);
        return NextResponse.json({
          success: true,
          message: 'Undid staging action.',
          item: target,
          items,
        });
      }
    }

    return NextResponse.json({
      success: true,
      message: 'Undo acknowledged.',
    });
  } catch (error: unknown) {
    return NextResponse.json(
      {
        success: false,
        message: error instanceof Error ? error.message : 'Undo failed.',
      },
      { status: 500 }
    );
  }
}
