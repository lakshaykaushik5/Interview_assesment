'use client'


import { useCallback, useRef, useState } from "react"

interface TranscriptMessage {
  message_type: 'PartialTranscript' | 'FinalTranscript';
  text: string;
  words?: Array<{
    text: string;
    start: number;
    end: number,
    confidence: number;
  }>;
}


export default function Page() {
  const [isRecording, setIsRecording] = useState<Boolean>(false)
  const [transcript, setTranscript] = useState<any>()
  const [partialTranscript, setPartialTranscript] = useState('')
  const [error, setError] = useState<string | null>(null)

  const wsRef = useRef<WebSocket | null>(null)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const streamRef = useRef<MediaStream | null>(null)

  const getToken = async () => {
    const response = await fetch('/api/assemblyai', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    })
    if (!response.ok) {
      throw new Error('Failed to get token')
    }

    const { token } = await response.json()
    alert(token + " here it is")
    return token
  }

  // const startRecording = useCallback(async () => {
  //   try {
  //     setError(null)

  //     const token = await getToken()
  //     //connecting to websocket


  //     const wsUrl = `wss://streaming.assemblyai.com/v3/ws?sample_rate=16000&formatted_finals=true&token=${token}`;
  //     const ws = new WebSocket(wsUrl);
  //     wsRef.current = ws

  //     ws.onopen = () => {
  //       console.log('WebSocket Connected')
  //       setIsRecording(true)
  //     }

  //     ws.onmessage = (event: any) => {
  //       const message: TranscriptMessage = JSON.parse(event.data)
  //       if (message.message_type === 'PartialTranscript') {
  //         setPartialTranscript(message.text)
  //       } else if (message.message_type === 'FinalTranscript') {
  //         setTranscript((prev: any) => prev + ' ' + message.text)
  //         setPartialTranscript('')
  //       }
  //     }

  //     ws.onerror = (error) => {
  //       console.error('WebSocket error :', error)
  //     }

  //     ws.onclose = () => {
  //       console.log('WebSocket Closed')
  //       setIsRecording(false)
  //     }

  //     const stream = await navigator.mediaDevices.getUserMedia({
  //       audio: {
  //         sampleRate: 1600,
  //         channelCount: 1,
  //         echoCancellation: true,
  //         noiseSuppression: true,
  //       }
  //     })

  //     streamRef.current = stream

  //     const mediaRecorder = new MediaRecorder(stream, {
  //       mimeType: 'audio/webm'
  //     })

  //     mediaRecorderRef.current = mediaRecorder

  //     mediaRecorder.ondataavailable = (event) => {
  //       if (event.data.size > 0 && ws.readyState === WebSocket.OPEN) {
  //         const reader = new FileReader()
  //         reader.onloadend = () => {
  //           const base64Audio = (reader.result as string).split(',')[1]
  //           ws.send(JSON.stringify({
  //             audio_data: base64Audio
  //           }))
  //         }
  //         reader.readAsDataURL(event.data)
  //       }
  //     }


  //     mediaRecorder.start(100)



  //   } catch (error) {
  //     console.error('Error starting recording: ', error)
  //     setError('Failed to start recording. Please check microphone permission. ')
  //   }
  // }, [])


  const startRecording = useCallback(async () => {
    try {
      setError(null);

      // 1. Get temporary token from your backend
      const token = await getToken();

      // 2. Ask for mic permission first
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: true
      });
      streamRef.current = stream;

      // 3. Connect to AssemblyAI WebSocket
      const wsUrl = `wss://streaming.assemblyai.com/v3/ws?sample_rate=16000&token=${token}`;
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log("✅ WebSocket Connected");
        setIsRecording(true);

        // 4. Start MediaRecorder only after WS is ready
        const mediaRecorder = new MediaRecorder(stream, { mimeType: "audio/webm" });
        mediaRecorderRef.current = mediaRecorder;

        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0 && ws.readyState === WebSocket.OPEN) {
            const reader = new FileReader();
            reader.onloadend = () => {
              const base64Audio = (reader.result as string).split(",")[1];
              ws.send(JSON.stringify({ audio_data: base64Audio }));
            };
            reader.readAsDataURL(event.data);
          }
        };

        mediaRecorder.start(250); // send every 250ms
      };

      ws.onmessage = (event) => {
        const msg: TranscriptMessage = JSON.parse(event.data);
        if (msg.message_type === "PartialTranscript") {
          setPartialTranscript(msg.text);
        } else if (msg.message_type === "FinalTranscript") {
          setTranscript((prev: any) => (prev ? prev + " " : "") + msg.text);
          setPartialTranscript("");
        }
      };

      ws.onerror = (err) => {
        console.error("WebSocket error:", err);
      };

      ws.onclose = () => {
        console.log("❌ WebSocket closed");
        setIsRecording(false);
      };

    } catch (err) {
      console.error("Error starting recording:", err);
      setError("Failed to start recording. Please check microphone permission.");
    }
  }, []);


  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop()  // ✅ Correct!
    }

    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop())
    }

    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.close()
    }

    setIsRecording(false)
    setPartialTranscript('')
  }, [])


  // const stopRecording = useCallback(() => {
  //   if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'inactive') {
  //     mediaRecorderRef.current.stop()
  //   }

  //   if (streamRef.current) {
  //     streamRef.current.getTracks().forEach(track => track.stop())
  //   }

  //   if (wsRef.current) {
  //     wsRef.current.close()
  //   }

  //   setIsRecording(false)
  //   setPartialTranscript('')
  // }, [])


  const clearTranscripts = () => {
    setTranscript('')
    setPartialTranscript('')
  }

  return (
    <div className="max-w-4xl max-auto p-6">
      <h1 className="text-3xl font-bold mb-6">
        Live Speech-to-text
      </h1>
      <div className="mb-6">
        <button onClick={isRecording ? stopRecording : startRecording} className={`px-6 py-3 rounded-lg font-semibold ${isRecording ? 'bg-red-500 hover:bg-red-600 text-white' : 'bg-blue-500 hover bg-blue-600 text-white'
          }`}>{isRecording ? 'Stop Recording' : 'Start Recording'}</button>
        <button onClick={clearTranscripts} className="ml-4 px-6 py-3 rounded-lg font-semibold bg-gray-500 hover:bg-gray-600 text-white">Clear</button>
      </div>
      {error && (
        <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}

      <div className="border rounded-lg p-4 min-h-32">
        <div className="text-gray-800">
          {transcript}
          {partialTranscript && (
            <span className="text-gray-500 italic"> {partialTranscript} </span>
          )}
        </div>
        {!transcript && !partialTranscript && (
          <div className="text-gray-400"> Click "Start Recording" to begin </div>
        )}
        {isRecording && (
          <div className="mt-4 flex items-center text-red-500">
            <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse mr-2"></div>
            Recording . . . .
          </div>
        )}
      </div>
    </div>
  )

}