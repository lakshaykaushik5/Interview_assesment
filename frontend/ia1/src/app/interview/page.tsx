// app/stream/page.tsx
"use client";

import React, { useCallback, useRef, useState } from "react";

type TranscriptMessage = {
  type?: "Begin" | "Turn" | "Termination" | string;
  id?: string;
  transcript?: string;
  turn_is_formatted?: boolean;
  // other fields possible depending on AssemblyAI response
};

export default function StreamPage() {
  const [isRecording, setIsRecording] = useState(false);
  const [partial, setPartial] = useState("");
  const [finalText, setFinalText] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [debug, setDebug] = useState<string>("");

  const wsRef = useRef<WebSocket | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const processorRef = useRef<ScriptProcessorNode | null>(null);
  const sourceRef = useRef<MediaStreamAudioSourceNode | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const tokenTimerRef = useRef<number | null>(null);

  // helper: downsample Float32Array to 16kHz
  function downsampleBuffer(buffer: Float32Array, inputSampleRate: number, outSampleRate = 16000) {
    if (outSampleRate === inputSampleRate) return buffer;
    const sampleRateRatio = inputSampleRate / outSampleRate;
    const newLength = Math.round(buffer.length / sampleRateRatio);
    const result = new Float32Array(newLength);
    let offsetResult = 0;
    let offsetBuffer = 0;
    while (offsetResult < newLength) {
      const nextOffsetBuffer = Math.round((offsetResult + 1) * sampleRateRatio);
      let accum = 0, count = 0;
      for (let i = offsetBuffer; i < nextOffsetBuffer && i < buffer.length; i++) {
        accum += buffer[i];
        count++;
      }
      result[offsetResult] = count ? accum / count : 0;
      offsetResult++;
      offsetBuffer = nextOffsetBuffer;
    }
    return result;
  }

  // helper: convert Float32Array -> PCM16 ArrayBuffer
  function floatTo16BitPCM(float32Array: Float32Array) {
    const buffer = new ArrayBuffer(float32Array.length * 2);
    const view = new DataView(buffer);
    let offset = 0;
    for (let i = 0; i < float32Array.length; i++, offset += 2) {
      let s = Math.max(-1, Math.min(1, float32Array[i]));
      view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7fff, true); // little endian
    }
    return buffer;
  }

  // get temporary streaming token from our backend
  const getToken = useCallback(async () => {
    const res = await fetch("/api/assemblyai");
    if (!res.ok) {
      const txt = await res.text();
      throw new Error("Failed to get token: " + txt);
    }
    const data = await res.json();
    return data.token as string;
  }, []);

  const startRecording = useCallback(async () => {
    setError(null);
    setDebug("");
    try {
      // basic support check
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        setError("getUserMedia not supported in this browser");
        return;
      }

      // 1) request microphone
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      // 2) get token
      const token = await getToken();

      // 3) open websocket to AssemblyAI (v3) with encoding parameter
      const wsUrl = `wss://streaming.assemblyai.com/v3/ws?sample_rate=16000&encoding=pcm_s16le&token=${token}`;
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;
      
      ws.onopen = () => {
        console.log('WS open');
        setDebug((d) => d + "WebSocket connected\n");
        // No need to send SessionBegins for v3 - session starts automatically
      };

      ws.onmessage = (evt) => {
        try {
          const msg: TranscriptMessage = JSON.parse(evt.data);
          
          switch (msg.type) {
            case "Begin":
              console.log('Session started:', msg.id);
              setDebug((d) => d + `Session started: ${msg.id}\n`);
              setIsRecording(true);
              break;
              
            case "Turn":
              if (msg.turn_is_formatted) {
                // Final transcript
                setFinalText((prev) => (prev ? prev + " " : "") + (msg.transcript || ""));
                setPartial("");
                setDebug((d) => d + "Final: " + (msg.transcript || "") + "\n");
              } else {
                // Partial transcript
                setPartial(msg.transcript || "");
              }
              break;
              
            case "Termination":
              console.log('Session terminated');
              setDebug((d) => d + "Session terminated\n");
              setIsRecording(false);
              break;
              
            default:
              console.log("Unknown message type:", msg.type);
              setDebug((d) => d + `Unknown message: ${msg.type}\n`);
          }
        } catch (e) {
          console.warn("Failed to parse ws message", e, evt.data);
          setDebug((d) => d + "Failed to parse message\n");
        }
      };

      ws.onerror = (err) => {
        console.error("WS error", err);
        setDebug((d) => d + "WS error\n");
      };

      ws.onclose = (ev) => {
        console.log("WS closed", ev);
        setDebug((d) => d + `WS closed: code=${ev.code} reason=${ev.reason}\n`);
        setIsRecording(false);
      };

      // 4) start WebAudio capture & processor
      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      audioContextRef.current = audioContext;

      // some browsers require a user gesture to resume context; we are in a click handler so OK
      if (audioContext.state === "suspended") {
        await audioContext.resume();
      }

      const source = audioContext.createMediaStreamSource(stream);
      sourceRef.current = source;

      // Create script processor (bufferSize 4096). Note: AudioWorklet is better but this is simpler.
      const bufferSize = 4096;
      const processor = audioContext.createScriptProcessor(bufferSize, 1, 1);
      processorRef.current = processor;

      // create a gain node to avoid audible output (connect processor->gain(0)->destination)
      const silentGain = audioContext.createGain();
      silentGain.gain.value = 0;

      processor.onaudioprocess = (e) => {
        try {
          const inputData = e.inputBuffer.getChannelData(0); // Float32Array
          // downsample to 16000
          const downsampled = downsampleBuffer(inputData, audioContext.sampleRate, 16000);
          // convert to 16-bit PCM
          const pcm16 = floatTo16BitPCM(downsampled);
          
          // send raw PCM data as binary WebSocket message (not JSON)
          if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            wsRef.current.send(pcm16);
          }
        } catch (err) {
          console.error("Audio processing error", err);
        }
      };

      // connect nodes
      source.connect(processor);
      processor.connect(silentGain);
      silentGain.connect(audioContext.destination);

      // optional: token refresh if you expect long sessions (token expiry). We'll set a timer to refresh token ~50 minutes for 1h token
      if (tokenTimerRef.current) {
        window.clearTimeout(tokenTimerRef.current);
        tokenTimerRef.current = null;
      }
      // refresh after 50 minutes (if using 3600s expiry)
      tokenTimerRef.current = window.setTimeout(async () => {
        try {
          setDebug((d) => d + "Refreshing token...\n");
          const newToken = await getToken();
          // Not all servers support "auth update" over opened ws. If required, close and reopen.
          console.log("new token", newToken);
        } catch (e) {
          console.warn("token refresh failed", e);
        }
      }, 50 * 60 * 1000);

      setDebug((d) => d + "Recording started\n");
    } catch (err: any) {
      console.error("startRecording error", err);
      setError(err?.message || String(err));
      setIsRecording(false);
    }
  }, [getToken]);

  const stopRecording = useCallback(() => {
    try {
      setDebug((d) => d + "Stopping...\n");

      // stop processor
      if (processorRef.current) {
        try {
          processorRef.current.disconnect();
        } catch { }
        processorRef.current.onaudioprocess = null;
        processorRef.current = null;
      }

      // stop source
      if (sourceRef.current) {
        try {
          sourceRef.current.disconnect();
        } catch { }
        sourceRef.current = null;
      }

      // close audio context
      if (audioContextRef.current) {
        try {
          audioContextRef.current.close();
        } catch { }
        audioContextRef.current = null;
      }

      // stop tracks
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((t) => t.stop());
        streamRef.current = null;
      }

      // send session termination and close socket
      if (wsRef.current) {
        try {
          if (wsRef.current.readyState === WebSocket.OPEN) {
            // Send proper termination message for v3
            wsRef.current.send(JSON.stringify({ type: "Terminate" }));
          }
        } catch (e) {
          console.warn("error sending termination", e);
        }
        try {
          wsRef.current.close();
        } catch { }
        wsRef.current = null;
      }

      if (tokenTimerRef.current) {
        window.clearTimeout(tokenTimerRef.current);
        tokenTimerRef.current = null;
      }

      setIsRecording(false);
      setDebug((d) => d + "Stopped\n");
    } catch (err) {
      console.error("stopRecording error", err);
      setError("Error stopping recording");
    }
  }, []);

  return (
    <div style={{ maxWidth: 800, margin: "0 auto", padding: 20 }}>
      <h2>AssemblyAI Realtime — Universal Streaming v3 (PCM16 16kHz)</h2>

      <div style={{ marginBottom: 12 }}>
        <button
          onClick={isRecording ? stopRecording : startRecording}
          style={{
            padding: "8px 16px",
            background: isRecording ? "#ef4444" : "#2563eb",
            color: "white",
            border: "none",
            borderRadius: 6,
            cursor: "pointer",
            marginRight: 10,
          }}
        >
          {isRecording ? "Stop" : "Start"}
        </button>

        <button
          onClick={() => {
            setFinalText("");
            setPartial("");
            setError(null);
            setDebug("");
          }}
          style={{
            padding: "8px 12px",
            background: "#6b7280",
            color: "white",
            border: "none",
            borderRadius: 6,
            cursor: "pointer",
          }}
        >
          Clear
        </button>
      </div>

      {error && (
        <div style={{ padding: 8, background: "#fee2e2", color: "#991b1b", borderRadius: 6 }}>
          Error: {error}
        </div>
      )}

      <div style={{ minHeight: 100, border: "1px solid #e5e7eb", padding: 12, borderRadius: 6 }}>
        <div style={{ fontSize: 14, color: "#111827" }}>{finalText}</div>
        {partial && <div style={{ fontStyle: "italic", color: "#6b7280" }}>{partial}</div>}
        {!finalText && !partial && <div style={{ color: "#9ca3af" }}>No transcript yet.</div>}
      </div>

      <pre style={{ marginTop: 12, whiteSpace: "pre-wrap", background: "#f8fafc", padding: 8, borderRadius: 6 }}>
        <strong>Debug:</strong>
        {"\n"}
        {debug}
      </pre>
    </div>
  );
}
