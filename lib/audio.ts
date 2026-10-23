'use client';

/**
 * Audio playback engine for Bee Wearable memo playback.
 * Combines Web Audio API dual-tone hardware chime with SpeechSynthesis narration.
 */

let activeStopFn: (() => void) | null = null;

export function stopAnyPlayingAudio(): void {
  if (activeStopFn) {
    activeStopFn();
    activeStopFn = null;
  }
}

export function playWearableAudioMemo(
  text: string,
  onStart?: () => void,
  onEnd?: () => void
): () => void {
  // Stop any other currently playing clip
  stopAnyPlayingAudio();

  let isCancelled = false;

  const stop = () => {
    isCancelled = true;
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
    onEnd?.();
  };

  activeStopFn = stop;
  onStart?.();

  // 1. Play authentic wearable chime via Web Audio API
  try {
    const AudioContextClass =
      typeof window !== 'undefined'
        ? window.AudioContext ||
          (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext
        : null;

    if (AudioContextClass) {
      const ctx = new AudioContextClass();
      if (ctx.state === 'suspended') {
        ctx.resume();
      }

      const now = ctx.currentTime;
      // Dual-tone frequency cue (D5 -> A5)
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      osc.type = 'sine';
      osc.frequency.setValueAtTime(587.33, now);
      osc.frequency.setValueAtTime(880, now + 0.08);

      gain.gain.setValueAtTime(0.09, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.24);

      osc.connect(gain);
      gain.connect(ctx.destination);

      osc.start(now);
      osc.stop(now + 0.25);
    }
  } catch (err) {
    console.warn('Web Audio API chime initialization:', err);
  }

  // 2. Play speech synthesis for the spoken quote
  if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.02;
    utterance.pitch = 1.0;

    const voices = window.speechSynthesis.getVoices();
    const voice = voices.find(
      (v) =>
        v.lang.startsWith('en') &&
        (v.name.includes('Natural') ||
          v.name.includes('Google') ||
          v.name.includes('Samantha') ||
          v.name.includes('Daniel') ||
          v.name.includes('Alex'))
    );
    if (voice) {
      utterance.voice = voice;
    }

    utterance.onend = () => {
      if (!isCancelled) {
        activeStopFn = null;
        onEnd?.();
      }
    };

    utterance.onerror = () => {
      if (!isCancelled) {
        activeStopFn = null;
        onEnd?.();
      }
    };

    // Small delay to allow the hardware chirp to complete naturally
    setTimeout(() => {
      if (!isCancelled) {
        window.speechSynthesis.speak(utterance);
      }
    }, 220);
  } else {
    // Fallback timer if speech synthesis is unavailable
    const timer = setTimeout(() => {
      if (!isCancelled) {
        activeStopFn = null;
        onEnd?.();
      }
    }, 4000);

    return () => {
      clearTimeout(timer);
      stop();
    };
  }

  return stop;
}
