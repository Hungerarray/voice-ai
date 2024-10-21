import asyncio
import pyaudio
import time
import tempfile
import wave

audio_queue = asyncio.Queue()

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 24000
CHUNK = 8000

# each time this get's called I want to store it in some wave file at temporary location
def mic_callback(input_data, frame_count, time_info, status_flag):
    audio_queue.put_nowait(input_data)
    # since our stream has no output, we can send None
    return (None, pyaudio.paContinue)


async def run():
    async def microphone(event: asyncio.Event):
        audio = pyaudio.PyAudio()
        stream = audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
            stream_callback=mic_callback,
        )

        await asyncio.sleep(5)
        event.set()

        stream.stop_stream()
        stream.close()

    async def save_wav(event: asyncio.Event):
        all_mic_data = []
        while True:
            mic_data = await audio_queue.get()
            all_mic_data.append(mic_data)

            if event.is_set() and audio_queue.empty():
                break
        
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
    tasks = [asyncio.create_task(i) for i in [microphone(event), save_wav(event)]]
    await asyncio.gather(*tasks)
    
    # adding VAD will take time, so we skip it for now
                


def main():
    asyncio.run(run())


if __name__ == "__main__":
    main()
