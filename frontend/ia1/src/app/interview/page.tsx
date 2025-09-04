'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Mic, MicOff } from 'lucide-react';
import { NextPage } from 'next';


declare global{
  interface Window{
    SpeechRecognition:any,
    webkitSpeechRecognition:any
  }
}
type SpeechRecognition = any;



const page: NextPage = () => {
  const [isUserSpeaking, setIsUserSpeaking] = useState(false);
  const [isAISpeaking, setIsAISpeaking] = useState(false);
  const [isClient, setIsClient] = useState(false);

  const [isListening,setIsListening] = useState(false)
  const [transcript,setTranscript] = useState("")
  const wsRef = useRef<SpeechRecognition | null>(null)

  useEffect(()=>{
    if(!("webkitSpeechRecognition" in window || "SpeechRecognition" in window)){
      alert("Speech Recognition API not supported in your Browser")
      return
    }

    //@ts-ignore
    const SpeechRecognitionClass = window.SpeechRecognition || window.webkitSpeechRecognition
    const recognition = new SpeechRecognitionClass()

    recognition.continuous = true
    recognition.interimResult = true

    recognition.lang = "en-US"
    recognition.maxAlternatives = 1

    recognition.current = recognition
  })

  useEffect(() => {
    setIsClient(true);
  }, []);

  const handleMicToggle = () => {
    if (isUserSpeaking) {
      setIsUserSpeaking(false);
      setTimeout(() => {
        setIsAISpeaking(true);
        setTimeout(() => setIsAISpeaking(false), 4000);
      }, 1000);
    } else if (!isAISpeaking) {
      setIsUserSpeaking(true);
    }
  };

  if (!isClient) {
    return <div className="bg-gray-900 min-h-screen"></div>;
  }

  const speakingColor = isUserSpeaking ? '#22c55e' : isAISpeaking ? '#3b82f6' : '#4b5563';

  return (
    <div className="min-h-screen bg-gray-900 text-white flex flex-col items-center justify-center p-6 overflow-hidden">
      <style>
        {`
          @keyframes sonar {
            0% {
              transform: scale(0.6);
              opacity: 0.8;
            }
            100% {
              transform: scale(2.5);
              opacity: 0;
            }
          }
          @keyframes breathe {
            0%, 100% {
              transform: scale(1);
            }
            50% {
              transform: scale(1.05);
            }
          }
        `}
      </style>

      <div className="relative w-96 h-96 flex items-center justify-center mb-12">
        {/* Sonar Waves */}
        {(isUserSpeaking || isAISpeaking) &&
          [...Array(4)].map((_, i) => (
            <div
              key={i}
              className="absolute rounded-full border-2"
              style={{
                borderColor: speakingColor,
                width: '10rem',
                height: '10rem',
                animation: `sonar 2.5s ${i * 0.6}s infinite ease-out`,
              }}
            />
          ))}

        {/* Central Button */}
        <button
          onClick={handleMicToggle}
          disabled={isAISpeaking}
          className={`relative w-28 h-28 rounded-full flex items-center justify-center text-white transition-all duration-300 transform shadow-2xl`}
          style={{
            backgroundColor: speakingColor,
            boxShadow: `0 0 40px 10px ${speakingColor}40`,
            animation: !(isUserSpeaking || isAISpeaking) ? `breathe 5s infinite ease-in-out` : 'none',
          }}
          aria-label={isUserSpeaking ? 'Stop recording' : 'Start recording'}
        >
          {isUserSpeaking ? <MicOff size={40} /> : <Mic size={40} />}
        </button>
      </div>

      <div className="text-center h-16 z-10">
        <h2 className="text-2xl font-medium text-gray-300 transition-opacity duration-300">
          {isUserSpeaking
            ? 'Listening...'
            : isAISpeaking
            ? 'AI is speaking...'
            : 'Click the mic to start'}
        </h2>
      </div>

      <div className="absolute bottom-6 text-xs text-gray-600 z-10">
        Minimalist Interview UI v2
      </div>
    </div>
  );
};

export default page;
