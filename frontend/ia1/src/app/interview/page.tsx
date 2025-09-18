// app/stream/page.tsx
"use client";

import React, { useCallback, useRef, useState, useEffect } from "react";

// Defines the shape of messages received from the WebSocket server
type AudioMessage = {
  type: "audio" | "text" | "error";
  data?: string;   // base64 audio data for the AI's voice
  text?: string;   // transcript or response text
  error?: string;
};

export default function StreamPage() {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [response, setResponse] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [debug, setDebug] = useState<string>("");

  // Refs to hold WebSocket, MediaRecorder, and other persistent objects
  const wsRef = useRef<WebSocket | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const silenceTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  
  // Refs for audio analysis
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const dataArrayRef = useRef<Uint8Array | null>(null);

  // Function to connect to the WebSocket backend
  const connectWebSocket = useCallback(() => {
    const wsUrl = `ws://localhost:8000/ws`; // Adjust if your backend URL is different
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      setDebug((d) => d + "WebSocket connection established.\n");
    };

    // This is the core logic for handling messages from the backend
    ws.onmessage = async (event) => {
      try {
        const message: AudioMessage = JSON.parse(event.data);
        
        // Handle transcribed text from user's speech
        if (message.type === 'text' && message.text) {
          setTranscript((prev) => prev + message.text + " ");
        } 
        // Handle audio data for the AI's response
        else if (message.type === 'audio' && message.data) {
          setResponse("AI is speaking...");
          await playAudioFromBase64(message.data);
          // Once audio finishes, you can update the response text if needed
          // Or wait for a final text message from the backend
        } 
        // Handle any errors from the backend
        else if (message.type === 'error') {
          setError(message.error || "An unknown error occurred.");
          setDebug((d) => d + `Error from backend: ${message.error}\n`);
        }
      } catch (e) {
        console.error("Failed to parse WebSocket message:", e);
        setDebug((d) => d + "Error parsing message from backend.\n");
      }
    };

    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
      setError("WebSocket connection failed.");
      setDebug((d) => d + "WebSocket error occurred.\n");
    };

    ws.onclose = (event) => {
      setDebug((d) => d + `WebSocket closed: ${event.code} ${event.reason}\n`);
      setIsRecording(false);
      setIsProcessing(false);
    };
  }, []);

  // Decodes base64 audio and plays it
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
      setDebug((d) => d + "Error playing base64 audio.\n");
    }
  };

  // Plays audio from an ArrayBuffer using the Web Audio API
  const playAudioFromArrayBuffer = async (arrayBuffer: ArrayBuffer) => {
    try {
      if (!audioContextRef.current) {
        audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
      }
      const audioContext = audioContextRef.current;

      // Resume context if it's suspended (required for autoplay policy)
      if (audioContext.state === 'suspended') {
        await audioContext.resume();
      }

      const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
      const source = audioContext.createBufferSource();
      source.buffer = audioBuffer;
      source.connect(audioContext.destination);
      source.start(0);
      setDebug((d) => d + "Playing AI audio response.\n");
    } catch (e) {
      console.error("Error playing audio:", e);
      setDebug((d) => d + "Error playing audio.\n");
    }
  };
  
  // Sends the accumulated audio chunks to the backend
  const sendAudioToBackend = useCallback(async () => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN || audioChunksRef.current.length === 0) {
      return;
    }

    try {
      setIsProcessing(true);
      setDebug((d) => d + "Sending audio to backend...\n");

      const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
      wsRef.current.send(audioBlob); // Send as binary blob

      setDebug((d) => d + `Sent ${audioBlob.size} bytes of audio.\n`);
      audioChunksRef.current = []; // Clear chunks after sending
    } catch (error) {
      console.error("Error sending audio:", error);
      setError("Failed to send audio to backend.");
      setIsProcessing(false);
    }
  }, []);


  
  // **FIXED**: This function now correctly detects sound from the microphone
  const isSoundDetected = useCallback(() => {
    if (!analyserRef.current || !dataArrayRef.current) {
      return false;
    }
    // This is the crucial missing piece: getting the audio data into the array
    analyserRef.current.getByteFrequencyData(dataArrayRef.current);

    // Calculate the average volume
    const sum = dataArrayRef.current.reduce((a, b) => a + b, 0);
    const average = sum / dataArrayRef.current.length;

    // A threshold of > 2 is sensitive enough for quiet speech
    return average > 10; 
  }, []);
  
  // Resets the silence timer
  const resetSilenceTimer = useCallback(() => {
    console.log(" ------------- timer reset ----------")
    if (silenceTimeoutRef.current) {
      clearTimeout(silenceTimeoutRef.current);
    }
    // After 2 seconds of silence, send the audio
    silenceTimeoutRef.current = setTimeout(() => {
      setDebug((d) => d + "Silence detected, processing audio...\n");
      sendAudioToBackend();
    }, 2000); // Using 2 seconds for quicker response
  }, [sendAudioToBackend]);


  const startRecording2 = useCallback(async ()=>{

    setError(null)
    setDebug("")
    setTranscript("")
    setResponse("")

    try {
      if (!navigator.mediaDevices?.getUserMedia) {
        setError("Your browser does not support audio recording.");
        return;
      }

      if (!wsRef.current || wsRef.current.readyState === WebSocket.CLOSED) {
        connectWebSocket();
      }

      const stream = await navigator.mediaDevices.getUserMedia({audio:true})
      const audioContext = new AudioContext()
      const source = audioContext.createMediaStreamSource(stream)

      await audioContext.audioWorklet.addModule('/audio-processor-worker.js')

      const processorNode = new AudioWorkletNode(audioContext,"audio-processor-worker")

      source.connect(processorNode)

      processorNode.connect(audioContext.destination)

      processorNode.port.onmessage = (event)=>{
        const rawAudioSamples = event.data
        if(wsRef.current?.readyState === WebSocket.OPEN){
          wsRef.current.send(rawAudioSamples.buffer)
        }
      }
      setIsRecording(true);
      setDebug("Recording started with AudioWorklet...");


      
    } catch (err:any) {
      console.error("Error starting recording:", err);
      setError(err?.message || "Could not start recording.");
      setIsRecording(false);
    }
  },[])

  const startRecording = useCallback(async () => {
    setError(null);
    setDebug("");
    setTranscript("");
    setResponse("");

    try {
      if (!navigator.mediaDevices?.getUserMedia) {
        setError("Your browser does not support audio recording.");
        return;
      }

      if (!wsRef.current || wsRef.current.readyState === WebSocket.CLOSED) {
        connectWebSocket();
      }

      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: 16000,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
        },
      });
      streamRef.current = stream;

      // Setup Web Audio API for volume analysis
      if (!audioContextRef.current) {
         audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
      }
      const source = audioContextRef.current.createMediaStreamSource(stream);
      analyserRef.current = audioContextRef.current.createAnalyser();
      analyserRef.current.fftSize = 256;
      source.connect(analyserRef.current);
      dataArrayRef.current = new Uint8Array(analyserRef.current.frequencyBinCount);

      audioChunksRef.current = [];
      const mimeType = 'audio/webm;codecs=opus';
      const mediaRecorder = new MediaRecorder(stream, { mimeType, audioBitsPerSecond: 128000 });
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
          // **FIXED**: Only reset the timer if sound is actually detected.
          // If it's silent, we let the timer run out to trigger processing.
          // console.log(event.data , " |||||||||||||||||||||||||||||||||||| ")
          if (isSoundDetected()) {
            console.log(" Sound detected")
             resetSilenceTimer();
          }
        }
      };

      mediaRecorder.onstop = () => {
        setDebug((d) => d + "Recording stopped.\n");
        if (audioChunksRef.current.length > 0) {
          sendAudioToBackend();
        }
      };

      // Start recording and the initial silence timer
      mediaRecorder.start(100); // Collect data every 250ms
      setIsRecording(true);
      resetSilenceTimer();
      setDebug("Recording started... speak now.\n");
    } catch (err: any) {
      console.error("Error starting recording:", err);
      setError(err?.message || "Could not start recording.");
      setIsRecording(false);
    }
  }, [connectWebSocket, resetSilenceTimer, sendAudioToBackend, isSoundDetected]);

  const stopRecording = useCallback(() => {
    try {
      if (silenceTimeoutRef.current) {
        clearTimeout(silenceTimeoutRef.current);
      }
      if (mediaRecorderRef.current?.state === "recording") {
        mediaRecorderRef.current.stop();
      }
      streamRef.current?.getTracks().forEach(track => track.stop());
      wsRef.current?.close();
      setIsRecording(false);
      setIsProcessing(false); // Ensure processing state is reset
    } catch (err) {
      console.error("Error stopping recording:", err);
      setError("Error stopping recording.");
    }
  }, []);

  // Cleanup on component unmount
  useEffect(() => {
    return () => {
      stopRecording();
      audioContextRef.current?.close();
    };
  }, [stopRecording]);

  return (
    <div style={{ maxWidth: 800, margin: "0 auto", padding: 20, fontFamily: 'sans-serif' }}>
      <h2>Voice AI Assistant - Speech to Speech</h2>

      <div style={{ marginBottom: 12 }}>
        <button
          onClick={isRecording ? stopRecording : startRecording2}
          disabled={isProcessing}
          style={{
            padding: "10px 18px",
            fontSize: 16,
            background: isRecording ? "#ef4444" : (isProcessing ? "#9ca3af" : "#2563eb"),
            color: "white",
            border: "none",
            borderRadius: 8,
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
            padding: "10px 18px",
            fontSize: 16,
            background: "#6b7280",
            color: "white",
            border: "none",
            borderRadius: 8,
            cursor: "pointer",
          }}
        >
          Clear
        </button>
      </div>

      {error && (
        <div style={{ padding: 12, background: "#fee2e2", color: "#991b1b", borderRadius: 6, marginBottom: 12 }}>
          <strong>Error:</strong> {error}
        </div>
      )}

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20, marginBottom: 12 }}>
        <div>
          <h3 style={{ margin: "0 0 8px 0", fontSize: 16 }}>Your Speech</h3>
          <div style={{ minHeight: 100, border: "1px solid #e5e7eb", padding: 12, borderRadius: 6, background: "#f9fafb" }}>
            {transcript || <span style={{ color: "#9ca3af" }}>Transcript will appear here...</span>}
          </div>
        </div>
        <div>
          <h3 style={{ margin: "0 0 8px 0", fontSize: 16 }}>AI Response</h3>
          <div style={{ minHeight: 100, border: "1px solid #e5e7eb", padding: 12, borderRadius: 6, background: "#f0f9ff" }}>
            {response || <span style={{ color: "#9ca3af" }}>AI response will appear here...</span>}
          </div>
        </div>
      </div>
      
      <div style={{ marginBottom: 12 }}>
        <div style={{ padding: 12, background: isRecording ? "#dcfce7" : "#f3f4f6", borderRadius: 6, textAlign: "center", fontSize: 14, fontWeight: "bold", color: isRecording ? "#166534" : "#374151" }}>
          {isRecording ? "🔴 Recording... (a 2-second pause will trigger processing)" :
           isProcessing ? "🔄 Processing your speech..." :
           "⭕ Ready to record"}
        </div>
      </div>

      <details style={{ marginTop: 20 }}>
        <summary style={{ cursor: "pointer", fontWeight: "bold", marginBottom: 8 }}>
          Debug Log
        </summary>
        <pre style={{ whiteSpace: "pre-wrap", background: "#f8fafc", padding: 12, borderRadius: 6, fontSize: 12, maxHeight: 200, overflow: "auto", border: "1px solid #e2e8f0" }}>
          {debug || "No debug information yet..."}
        </pre>
      </details>
    </div>
  );
}