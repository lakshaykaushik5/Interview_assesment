import grpc
import asyncio
import os

# from generated import audio_pb2, audio_pb2_grpc
# from generated import audio_pb2 as audio_pb2
# from generated import audio_pb2_grpc as audio_pb2_grpc
from generated import audio_pb2,audio_pb2_grpc

from assemblyai.streaming.v3 import (
    StreamingClient,
    StreamingParameters,
    StreamingEvents,
    StreamingClientOptions,
    BeginEvent,
    TurnEvent,
    TerminationEvent,
    StreamingError
)
import numpy as np
from pydub import AudioSegment


from dotenv import load_dotenv ,find_dotenv
import io

load_dotenv(find_dotenv())


import numpy as np

def float32_to_int16_pcm(float32_bytes: bytes) -> bytes:
    float32_samples = np.frombuffer(float32_bytes, dtype=np.float32)
    int16_samples = (float32_samples * 32767).astype(np.int16)
    return int16_samples.tobytes()


def convert_to_16k_mono_pcm(audio_bytes, input_format="wav"):
    """
    Convert input audio bytes (e.g. wav/mp3) to 16kHz mono 16-bit PCM raw bytes.
    Requires ffmpeg installed on system for pydub.
    """
    audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format=input_format)
    audio = audio.set_channels(1).set_frame_rate(16000)
    return audio.raw_data


class SpeechToTextServicer(audio_pb2_grpc.SpeechToTextServicer):
    def Transcribe(self, request_iterator, context):
        # Create choices for event/callbacks as you prefer -- here just logging.
        def on_begin(client, event): print("Session Started:", event.id)
        
        def on_turn(client, event):
            nonlocal output_transcripts
            # print(event," --------------------- ")
            if hasattr(event, 'end_of_turn') :  # or event.final or equivalent
                print(event.end_of_turn," -------------------")
                if event.end_of_turn is True:
                    print("Final turn transcript:", event.transcript , " ------> ",event.end_of_turn," || ",type(event.transcript)," ||")
                    output_transcripts = event.transcript
                # Send this finalized transcript to frontend, overwrite previous partial
 
            # print("Transcript update:", event.transcript,"-----\n\n\n",event.words)


        def on_termination(client, event): print("Terminated after",  "final transcripts")
        def on_error(client, error): print(f"Error: {error}")   

        client = StreamingClient(
            StreamingClientOptions(
                api_key=os.getenv("ASSEMBLYAI_API_KEY"),
                api_host="streaming.assemblyai.com"
        ))
        client.on(StreamingEvents.Begin, on_begin)
        client.on(StreamingEvents.Turn, on_turn)
        client.on(StreamingEvents.Termination, on_termination)
        client.on(StreamingEvents.Error, on_error)

        client.connect(
            StreamingParameters(
                sample_rate=16000,
                format_turns=True
            )
        )

        try:
            for request in request_iterator:
                print("Audio chunk received at", request.timestamp)
                pcm_audio = float32_to_int16_pcm(request.audio_data)


                client.stream(pcm_audio)
                # client.stream(request.audio_data)
                # Optionally: Yield confirmation for each chunk
                if output_transcripts:
                    print(output_transcripts,"============= output transcripts =============")
                    reply = audio_pb2.Transcript(output_transcripts)
                    yield reply

                    output_transcripts = ""
        finally:
            client.disconnect(terminate=True)

async def main_server():
    server = grpc.aio.server()
    audio_pb2_grpc.add_SpeechToTextServicer_to_server(SpeechToTextServicer(), server)
    server.add_insecure_port("[::]:50061")
    await server.start()
    print("gRPC server started on port 50061")
    await server.wait_for_termination()

if __name__ == "__main__":
    asyncio.run(main_server())
