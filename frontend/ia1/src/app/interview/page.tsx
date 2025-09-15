// app/stream/page.tsx
"use client";

import React, { useCallback, useRef, useState, useEffect } from "react";

type AudioMessage = {
  type: "audio" | "text" | "error";
  data?: string; // base64 audio data
  text?: string; // transcript or response text
  error?: string;
};

export default function StreamPage() {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [response, setResponse] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [debug, setDebug] = useState<string>("");

  const wsRef = useRef<WebSocket | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const silenceTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);

  // Initialize WebSocket connection to your backend
  const connectWebSocket = useCallback(() => {
    const wsUrl = `ws://localhost:8000/ws`; // Adjust URL as needed
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      setDebug((d) => d + "Connected to backend WebSocket\n");
    };

    ws.onmessage = async (event) => {
      try {
        // Handle both text and binary messages

        console.log(" --- was here - on message")
        if (typeof event.data === "string") {
          const message: AudioMessage = JSON.parse(event.data);
          
          switch (message.type) {
            case "text":
              if (message.text?.includes("transcript:")) {
                setTranscript(message.text.replace("transcript:", ""));
              } else {
                setResponse(message.text || "");
              }
              break;
              
            case "audio":
              await playAudioFromBase64(message.data || "");
              break;
              
            case "error":
              setError(message.error || "Unknown error");
              break;
          }
        } else {
          // Handle binary audio data
          await playAudioFromArrayBuffer(event.data);
        }
        
        setIsProcessing(false);
      } catch (e) {
        console.error("Error handling WebSocket message:", e);
        setDebug((d) => d + "Error parsing WebSocket message\n");
      }
    };

    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
      setError("WebSocket connection error");
      setDebug((d) => d + "WebSocket error\n");
    };

    ws.onclose = (event) => {
      setDebug((d) => d + `WebSocket closed: ${event.code} ${event.reason}\n`);
      setIsRecording(false);
      setIsProcessing(false);
    };
  }, []);

  // Play audio from base64 string
  const playAudioFromBase64 = async (base64Data: string) => {
    try {
      const binaryString = window.atob(base64Data);
      const len = binaryString.length;
      const bytes = new Uint8Array(len);
      for (let i = 0; i < len; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }
      await playAudioFromArrayBuffer(bytes.buffer);
    } catch (e) {
      console.error("Error playing base64 audio:", e);
      setDebug((d) => d + "Error playing base64 audio\n");
    }
  };

  // Play audio from ArrayBuffer
  const playAudioFromArrayBuffer = async (arrayBuffer: ArrayBuffer) => {
    try {
      if (!audioContextRef.current) {
        audioContextRef.current = new AudioContext();
      }
      
      const audioContext = audioContextRef.current;
      
      if (audioContext.state === 'suspended') {
        await audioContext.resume();
      }

      const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
      const source = audioContext.createBufferSource();
      source.buffer = audioBuffer;
      source.connect(audioContext.destination);
      source.start(0);
      
      setDebug((d) => d + "Playing audio response\n");
    } catch (e) {
      console.error("Error playing audio:", e);
      setDebug((d) => d + "Error playing audio\n");
    }
  };

  // Send accumulated audio chunks to backend
  const sendAudioToBackend = useCallback(async () => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN || audioChunksRef.current.length === 0) {
      return;
    }

    try {
      setIsProcessing(true);
      setDebug((d) => d + "Sending audio to backend for processing...\n");

      const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
      const arrayBuffer = await audioBlob.arrayBuffer();
      
      // Send binary audio data
      console.log( " ------------- here sending audio file --------------")
      wsRef.current.send(arrayBuffer);
      
      setDebug((d) => d + `Sent ${audioBlob.size} bytes of audio data\n`);
      
      // Clear chunks after sending
      audioChunksRef.current = [];
    } catch (error) {
      console.error("Error sending audio:", error);
      setError("Failed to send audio to backend");
      setIsProcessing(false);
    }
  }, []);

  // Reset silence timer
  const resetSilenceTimer = useCallback(() => {
    if (silenceTimeoutRef.current) {
      clearTimeout(silenceTimeoutRef.current);
    }
    
    // Set 5-second silence detection
    silenceTimeoutRef.current = setTimeout(() => {
      setDebug((d) => d + "5-second silence detected, processing audio...\n");
      sendAudioToBackend();
    }, 5000);
  }, [sendAudioToBackend]);

  const startRecording = useCallback(async () => {
    setError(null);
    setDebug("");
    setTranscript("");
    setResponse("");

    console.log(" here in recording function --------------------")

    try {
      if (!navigator.mediaDevices?.getUserMedia) {
        setError("getUserMedia not supported");
        return;
      }

      // Connect WebSocket if not already connected
      if (!wsRef.current || wsRef.current.readyState === WebSocket.CLOSED) {
        connectWebSocket();
      }

      // Get microphone stream
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: 16000,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true
        }
      });

      console.log(" here 111111 ",stream)
      
      streamRef.current = stream;
      audioChunksRef.current = [];

      // Setup MediaRecorder
      const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus') 
        ? 'audio/webm;codecs=opus' 
        : 'audio/webm';

      console.log(" here 222222 ",mimeType)
        
      const mediaRecorder = new MediaRecorder(stream, { 
        mimeType,
        audioBitsPerSecond: 128000
      });
      
      mediaRecorderRef.current = mediaRecorder;

      console.log(" here 3333333333333333", mediaRecorder)

      mediaRecorder.ondataavailable = (event) => {
        // console.log(" here 444444444444 ",event)
        if (event.data && event.data.size > 0) {
          audioChunksRef.current.push(event.data);
          console.log(" here 555555555555555555",event.data)
          resetSilenceTimer();
          setDebug((d) => d + `Audio chunk recorded: ${event.data.size} bytes\n`);
        }
      };

      mediaRecorder.onerror = (event) => {
        console.error("MediaRecorder error:", event);
        setError("Recording error occurred");
      };

      mediaRecorder.onstop = () => {
        setDebug((d) => d + "Recording stopped\n");
        if (audioChunksRef.current.length > 0) {
          sendAudioToBackend();
        }
      };

      // Start recording with small time slices for better silence detection
      mediaRecorder.start(100);
      setIsRecording(true);
      setDebug((d) => d + "Recording started - speak now (5 sec pause will trigger processing)\n");

    } catch (err: any) {
      console.error("Error starting recording:", err);
      setError(err?.message || String(err));
      setIsRecording(false);
    }
  }, [connectWebSocket, resetSilenceTimer]);

  const stopRecording = useCallback(() => {
    try {
      // Clear silence timer
      if (silenceTimeoutRef.current) {
        clearTimeout(silenceTimeoutRef.current);
        silenceTimeoutRef.current = null;
      }

      // Stop media recorder
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
        mediaRecorderRef.current.stop();
      }

      // Stop media stream
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
        streamRef.current = null;
      }

      // Close WebSocket
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.close();
      }

      setIsRecording(false);
      setDebug((d) => d + "Recording stopped\n");
    } catch (err) {
      console.error("Error stopping recording:", err);
      setError("Error stopping recording");
    }
  }, []);

  // Cleanup on component unmount
  useEffect(() => {
    return () => {
      stopRecording();
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
    };
  }, [stopRecording]);

  return (
    <div style={{ maxWidth: 800, margin: "0 auto", padding: 20 }}>
      <h2>Voice AI Assistant - Speech to Speech</h2>
      
      <div style={{ marginBottom: 12 }}>
        <button
          onClick={isRecording ? stopRecording : startRecording}
          disabled={isProcessing}
          style={{
            padding: "8px 16px",
            background: isRecording ? "#ef4444" : (isProcessing ? "#9ca3af" : "#2563eb"),
            color: "white",
            border: "none",
            borderRadius: 6,
            cursor: isProcessing ? "not-allowed" : "pointer",
            marginRight: 10,
          }}
        >
          {isProcessing ? "Processing..." : (isRecording ? "Stop Recording" : "Start Recording")}
        </button>

        <button
          onClick={() => {
            setTranscript("");
            setResponse("");
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
        <div style={{ 
          padding: 12, 
          background: "#fee2e2", 
          color: "#991b1b", 
          borderRadius: 6,
          marginBottom: 12
        }}>
          <strong>Error:</strong> {error}
        </div>
      )}

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 12 }}>
        <div>
          <h3 style={{ margin: "0 0 8px 0", fontSize: 16 }}>Transcript</h3>
          <div style={{ 
            minHeight: 80, 
            border: "1px solid #e5e7eb", 
            padding: 12, 
            borderRadius: 6,
            background: "#f9fafb"
          }}>
            {transcript || <span style={{ color: "#9ca3af" }}>Your speech will appear here...</span>}
          </div>
        </div>

        <div>
          <h3 style={{ margin: "0 0 8px 0", fontSize: 16 }}>AI Response</h3>
          <div style={{ 
            minHeight: 80, 
            border: "1px solid #e5e7eb", 
            padding: 12, 
            borderRadius: 6,
            background: "#f0f9ff"
          }}>
            {response || <span style={{ color: "#9ca3af" }}>AI response will appear here...</span>}
          </div>
        </div>
      </div>

      <div style={{ marginBottom: 12 }}>
        <div style={{
          padding: 8,
          background: isRecording ? "#dcfce7" : "#f3f4f6",
          borderRadius: 6,
          textAlign: "center",
          fontSize: 14,
          fontWeight: "bold",
          color: isRecording ? "#166534" : "#374151"
        }}>
          {isRecording ? "🔴 Recording... (5 sec pause will trigger processing)" : 
           isProcessing ? "🔄 Processing your speech..." : 
           "⭕ Ready to record"}
        </div>
      </div>

      <details style={{ marginTop: 12 }}>
        <summary style={{ cursor: "pointer", fontWeight: "bold", marginBottom: 8 }}>
          Debug Log
        </summary>
        <pre style={{ 
          whiteSpace: "pre-wrap", 
          background: "#f8fafc", 
          padding: 12, 
          borderRadius: 6,
          fontSize: 12,
          maxHeight: 200,
          overflow: "auto",
          border: "1px solid #e2e8f0"
        }}>
          {debug || "No debug information yet..."}
        </pre>
      </details>

      <div style={{ marginTop: 20, fontSize: 14, color: "#6b7280" }}>
        <h4>How to use:</h4>
        <ol>
          <li>Click "Start Recording" to begin</li>
          <li>Speak naturally into your microphone</li>
          <li>Pause for 5 seconds to automatically trigger processing</li>
          <li>Your speech will be transcribed, processed by AI, and played back</li>
          <li>Click "Stop Recording" to end the session</li>
        </ol>
      </div>
    </div>
  );
}
