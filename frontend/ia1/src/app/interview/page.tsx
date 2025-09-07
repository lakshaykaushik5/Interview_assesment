'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, Send, Trash2, Volume2 } from 'lucide-react';
import { NextPage } from 'next';

// Global declarations
declare global {
  interface Window {
    SpeechRecognition: any;
    webkitSpeechRecognition: any;
  }
}

interface Message {
  id: string;
  type: 'user' | 'ai';
  text: string;
  timestamp: Date;
}

const Page: NextPage = () => {
  const [isListening, setIsListening] = useState(false);
  const [isAISpeaking, setIsAISpeaking] = useState(false);
  const [isClient, setIsClient] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [conversationStarted, setConversationStarted] = useState(false);

  const recognitionRef = useRef<any>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setIsClient(true);
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Initialize Speech Recognition
  useEffect(() => {
    if (!isClient) return;

    if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
      console.error('Speech Recognition API not supported in this browser');
      return;
    }

    const SpeechRecognitionClass = window.SpeechRecognition || window.webkitSpeechRecognition;
    let recognition = new SpeechRecognitionClass();

    let restarting = false
    let stoppedByApp = false
    let startedOnce = false
    let restartTimer : number|null = null

    let sessionFinal = ''

    const startRecognition = ()=>{
      try {
        if(!recognition)return

        recognition.continous = true
        recognition.interimResults = true
        recognition.lang = 'en-US'
        recognition.maxAlternatives = 1
        recognition.start()
        setIsListening(true)
        restarting = false
      } catch (error) {
        if(!restarting){
          restarting = true
          restartTimer = window.setTimeout(()=>{
            restarting = false
            startRecognition()
          },5000)
        }
      }
    }

    recognition.onstart = ()=>{
      startedOnce = true
    }


    // recognition.continuous = true;
    // recognition.interimResults = true;
    // recognition.lang = 'en-US';
    // recognition.maxAlternatives = 1;

    recognition.onresult = async (event: any) => {
      let interimTranscript = '';
      // let finalTranscript = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i];
        if (result.isFinal) {
          sessionFinal += result[0].transcript;
        } else {
          interimTranscript += result[0].transcript;
        }
      }

      setTranscript((sessionFinal + interimTranscript).trim());

      if(event.results[event.results.length-1]?.isFinal){
        const newChunk = sessionFinal.trim()
        handleUserMessage(newChunk)
      }

      // if (finalTranscript) {
      //   handleUserMessage(finalTranscript.trim());
      //   setTranscript('');
      // }
    };

    recognition.onerror = (event: any) => {
      console.error('Speech recognition error:', event.error);
      if(event.error === 'not-allowed' || event.error === 'service-not-allowed'){
        stoppedByApp=true
        setIsListening(false)
        return
      }

      if(event.error === 'no-speech' && !startedOnce){
        recognition.onresult = null as any
        recognition.onerror = null as any
        recognition.onend = null as any
        recognition = new SpeechRecognitionClass()
      }
    };

    recognition.onend = () => {
      setIsListening(false);
      if(stoppedByApp)return;
      if(!restarting){
        restarting=true
        restartTimer = window.setTimeout(()=>{
          restarting=false
          startRecognition()
        },5000)
      }
    };

    recognitionRef.current = recognition;
    stoppedByApp = false
    startRecognition()
    return () => {
      stoppedByApp=true
      if(restartTimer)window.clearTimeout(restartTimer)
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch  {
          
        }
      }
    };
  }, [isClient]);

  const startConversation = () => {
    setConversationStarted(true);
    addMessage('ai', "Hello! I'm your AI assistant. How can I help you today?");
  };

  const addMessage = (type: 'user' | 'ai', text: string) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      type,
      text,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, newMessage]);
  };

  const handleUserMessage = async (text: string) => {
    if (!text.trim()) return;

    addMessage('user', text);
    setIsProcessing(true);

    // Simulate AI processing delay
    setTimeout(() => {
      const aiResponse = generateAIResponse(text);
      addMessage('ai', aiResponse);
      setIsProcessing(false);

      // Optional: Speak the AI response
      speakText(aiResponse);
    }, 1000 + Math.random() * 2000);
  };

  const generateAIResponse = (userMessage: string): string => {
    // Simple AI response simulation - replace with actual AI API call
    const responses = [
      "That's an interesting point. Can you tell me more about that?",
      "I understand what you're saying. Let me think about this for a moment.",
      "Thank you for sharing that with me. What would you like to explore next?",
      "That's a great question! Here's what I think about it...",
      "I see where you're coming from. Let's dive deeper into this topic.",
    ];
    return responses[Math.floor(Math.random() * responses.length)];
  };

  const speakText = (text: string) => {
    return 
    if ('speechSynthesis' in window) {
      setIsAISpeaking(true);
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.8;
      utterance.pitch = 1;
      utterance.volume = 0.8;

      utterance.onend = () => {
        setIsAISpeaking(false);
      };

      window.speechSynthesis.speak(utterance);
    }
  };

  const startListening = () => {
    if (recognitionRef.current && !isListening) {
      setIsListening(true);
      recognitionRef.current.start();
    }
  };

  const stopListening = () => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    }
  };

  const handleMicToggle = () => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  };

  const clearConversation = () => {
    setMessages([]);
    setConversationStarted(false);
    setTranscript('');
  };

  const handleSendMessage = () => {
    if (transcript.trim()) {
      handleUserMessage(transcript.trim());
      setTranscript('');
    }
  };

  if (!isClient) {
    return <div className="bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 min-h-screen"></div>;
  }

  if (!conversationStarted) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 text-white flex flex-col items-center justify-center p-6">
        <style jsx>{`
          @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-20px); }
          }
          @keyframes glow {
            0%, 100% { box-shadow: 0 0 20px rgba(59, 130, 246, 0.5); }
            50% { box-shadow: 0 0 40px rgba(59, 130, 246, 0.8); }
          }
        `}</style>

        <div className="text-center mb-12 animate-float">
          <h1 className="text-6xl font-bold mb-4 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
            AI Companion
          </h1>
          <p className="text-xl text-gray-300 mb-8">
            Your intelligent conversation partner
          </p>
        </div>

        <button
          onClick={startConversation}
          className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-semibold py-4 px-12 rounded-full text-xl transition-all duration-300 transform hover:scale-105 animate-glow"
        >
          Start Conversation
        </button>

        <div className="absolute bottom-6 text-sm text-gray-400">
          Click to begin your AI conversation experience
        </div>
      </div>
    );
  }

  const speakingColor = isListening ? '#10b981' : isAISpeaking ? '#3b82f6' : '#6b7280';

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 text-white flex flex-col">
      <style jsx>{`
        @keyframes pulse-ring {
          0% { transform: scale(0.33); }
          40%, 50% { opacity: 1; }
          100% { opacity: 0; transform: scale(1.33); }
        }
        @keyframes pulse-dot {
          0% { transform: scale(0.8); }
          50% { transform: scale(1); }
          100% { transform: scale(0.8); }
        }
      `}</style>

      {/* Header */}
      <div className="bg-black/20 backdrop-blur-sm border-b border-white/10 p-4 flex justify-between items-center">
        <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
          AI Conversation
        </h1>
        <button
          onClick={clearConversation}
          className="p-2 hover:bg-white/10 rounded-lg transition-colors"
          title="Clear conversation"
        >
          <Trash2 size={20} />
        </button>
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs lg:max-w-md px-4 py-3 rounded-2xl ${message.type === 'user'
                  ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white'
                  : 'bg-white/10 backdrop-blur-sm border border-white/20 text-gray-100'
                }`}
            >
              <p className="text-sm leading-relaxed">{message.text}</p>
              <p className="text-xs opacity-70 mt-1">
                {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </p>
            </div>
          </div>
        ))}

        {isProcessing && (
          <div className="flex justify-start">
            <div className="bg-white/10 backdrop-blur-sm border border-white/20 text-gray-100 max-w-xs lg:max-w-md px-4 py-3 rounded-2xl">
              <div className="flex items-center space-x-2">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
                <span className="text-sm text-gray-300">AI is thinking...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="bg-black/20 backdrop-blur-sm border-t border-white/10 p-4">
        {/* Current transcript display */}
        {transcript && (
          <div className="mb-3 p-3 bg-white/10 rounded-lg border border-white/20">
            <p className="text-sm text-gray-300">
              <span className="text-blue-400">Speaking:</span> {transcript}
            </p>
          </div>
        )}

        <div className="flex items-center space-x-4">
          {/* Voice input button */}
          <div className="relative">
            {(isListening || isAISpeaking) && (
              <div className="absolute inset-0">
                <div
                  className="h-12 w-12 flex items-center justify-center rounded-full border opacity-75 animate-pulse-ring"
                  style={{ borderColor: speakingColor, animationDuration: '1.5s' }}
                ></div>
              </div>
            )}
            <div className='w-full flex justify-center'>
              <button
                onClick={handleMicToggle}
                disabled={isAISpeaking || isProcessing}
                className="relative w-12 h-12 rounded-full flex items-center justify-center transition-all duration-200 transform hover:scale-105 disabled:opacity-50"
                style={{
                  backgroundColor: speakingColor,
                  boxShadow: `0 4px 20px ${speakingColor}40`,
                  animation: isListening ? 'pulse-dot 1.5s infinite' : 'none',
                }}
                title={isListening ? 'Stop listening' : 'Start voice input'}
              >
                {isListening ? <MicOff size={20} /> : <Mic size={20} />}
              </button>
            </div>
          </div>

          {/* Send button */}

        </div>

        {/* Status indicator */}
        <div className="mt-3 text-center">
          <p className="text-xs text-gray-400">
            {isListening ? (
              <span className="text-green-400">🎤 Listening...</span>
            ) : isAISpeaking ? (
              <span className="text-blue-400">🔊 AI Speaking...</span>
            ) : isProcessing ? (
              <span className="text-yellow-400">⏳ Processing...</span>
            ) : (
              'Click mic to speak or type your message'
            )}
          </p>
        </div>
      </div>
    </div>
  );
};

export default Page;
