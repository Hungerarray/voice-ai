import asyncio
import pyaudio
import webrtcvad
import collections
from enum import Enum
import math
import tempfile
import wave

audio_queue = asyncio.Queue()

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
# A chunk is the number of frames in a buffer, if we want 30ms duration frames, 
# Chunk size =  (0.03 * RATE) Frames
MS_IN_SEC = 1000
VAD_FRAME_MS = 30
VAD_WINDOW_S = 1
VAD_ACTIVATION_RATE = 0.5

CHUNK = math.ceil(VAD_FRAME_MS / MS_IN_SEC * RATE)
VAD_BUFF_MAX_LEN = math.ceil(VAD_WINDOW_S * MS_IN_SEC / VAD_FRAME_MS)


# each time this get's called I want to store it in some wave file at temporary location
def mic_callback(input_data, frame_count, time_info, status_flag):
    audio_queue.put_nowait(input_data)
    # since our stream has no output, we can send None
    return (None, pyaudio.paContinue)

class SpeechState(Enum):
    NOT_SPEAKING = 2
    SPEAKING = 1

async def run():
    async def microphone(event: asyncio.Event):
        audio = pyaudio.PyAudio() # if we are running in a loop, we probably want to move it outside
        # we can open as many streams but doesn't make sense to initialize PyAudio every iteration
        stream = audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
            stream_callback=mic_callback,
        )

        # doing event.wait() freezes all 
        while not event.is_set():
            await asyncio.sleep(0.01)

        stream.stop_stream()
        stream.close()

    # We need to create a state machine here
    async def mic_receive(event: asyncio.Event):
        all_mic_data = []
        speech_state = SpeechState.NOT_SPEAKING
        vad_buff = collections.deque(maxlen=VAD_BUFF_MAX_LEN)
        vad = webrtcvad.Vad()

        # VAD code must be set here
        # Initially we are in not speaking state
        while True:
            mic_data = await audio_queue.get()
            is_speech = vad.is_speech(mic_data, RATE)
            print(f"Current state: {speech_state}")
            
            # we don't start "Listening" until we have confirmed 50% or more of voiced frames in past 1 second
            if speech_state == SpeechState.NOT_SPEAKING:
                vad_buff.append((mic_data, is_speech)) 
                num_voiced = sum([1 for _, speech in vad_buff if speech])
                if num_voiced >= VAD_ACTIVATION_RATE * VAD_BUFF_MAX_LEN:
                    speech_state = SpeechState.SPEAKING
                    for f, _ in vad_buff:
                        all_mic_data.append(f)
                    vad_buff.clear()
            # We stop "Listening" when we have had 50% or more unvoiced frames in past 1 second
            elif speech_state == SpeechState.SPEAKING:
                all_mic_data.append(mic_data)
                vad_buff.append((mic_data, is_speech))
                num_unvoiced = sum([1 for _, speech in vad_buff if not speech])
                if num_unvoiced >= VAD_ACTIVATION_RATE * VAD_BUFF_MAX_LEN:
                    break
            
            audio_queue.task_done()

        # We terminate the "Listening" phase
        event.set()
        while not audio_queue.empty():
            audio_queue.get_nowait()
            audio_queue.task_done() 
        
        # make temp wav file    
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tp:
            wav = wave.open(tp, 'wb')
            wav.setnchannels(CHANNELS)
            wav.setsampwidth(pyaudio.get_sample_size(FORMAT))
            wav.setframerate(RATE)
            wav.writeframes(b"".join(all_mic_data))
            wav.close()
            print(f"written {len(all_mic_data)}")
            print(f"wave file written to {tp.name}")
            
    event = asyncio.Event()
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(i) for i in [microphone(event), mic_receive(event)]]

def main():
    asyncio.run(run())


if __name__ == "__main__":
    main()
