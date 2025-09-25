/// <reference lib="webworker" />

// This is the threshold for silence. You may need to adjust this value
// based on your microphone's sensitivity and background noise.
const SILENCE_THRESHOLD = 0.01;

/**
 * Calculates the Root Mean Square (RMS) of an audio buffer to measure its volume.
 * @param {Float32Array} channel - The audio data for a single channel.
 * @returns {number} The RMS value of the buffer.
 */
function getRms(channel) {
  let sumOfSquares = 0;
  for (let i = 0; i < channel.length; i++) {
    sumOfSquares += channel[i] * channel[i];
  }
  const meanSquare = sumOfSquares / channel.length;
  return Math.sqrt(meanSquare);
}

class AudioProcessor extends AudioWorkletProcessor {
  constructor(options) {
    super();
    this.sampleRate = options.processorOptions.sampleRate || 16000;
    this.bufferSize = this.sampleRate * 0.100; // 100ms buffer
    this.buffer = new Float32Array(this.bufferSize);
    this.currentPosition = 0;
  }

  process(inputs) {
    const input = inputs[0];
    const channel = input[0];

    if (!channel) {
      return true;
    }

    // Calculate the volume of the incoming chunk.
    const volume = getRms(channel);

    // **THE KEY CHANGE**: Only process and buffer the audio if it's NOT silent.
    if (volume > SILENCE_THRESHOLD) {
      // The buffering logic from before
      const remainingSpace = this.bufferSize - this.currentPosition;
      if (channel.length <= remainingSpace) {
        this.buffer.set(channel, this.currentPosition);
        this.currentPosition += channel.length;
      } else {
        const firstPart = channel.subarray(0, remainingSpace);
        this.buffer.set(firstPart, this.currentPosition);

        this.port.postMessage(this.buffer);

        const secondPart = channel.subarray(remainingSpace);
        this.buffer.fill(0);
        this.buffer.set(secondPart, 0);
        this.currentPosition = secondPart.length;
      }
    }

    return true;
  }
}

registerProcessor('audio-processor-worker', AudioProcessor);