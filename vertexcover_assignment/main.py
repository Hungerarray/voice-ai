import asyncio
import os
import tempfile
import time

import pyaudio
import voiceai.listener
import voiceai.stt

def main():
    pa = pyaudio.PyAudio()
    deepgram_key = os.getenv("DEEPGRAM_API_KEY")

    lis = voiceai.listener.Listener(pa)
    tts = voiceai.stt.DeepGramSTT(deepgram_key)

    print("listening")
    audio = asyncio.run(lis.run())
    print("Audio obtained")
    
    print("sending to deepgram")
    start_time = time.perf_counter()
    jsonstr = tts.convert(audio)
    print(f"obtained response from deepgram in, {time.perf_counter() - start_time} seconds")

    print(jsonstr)

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tp:
        tp.write(audio)
        print(f"wave file written to {tp.name}")

if __name__ == "__main__":
    main()
