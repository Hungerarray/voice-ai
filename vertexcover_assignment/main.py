import asyncio
import tempfile
import wave

import pyaudio
import voiceai.listener

def main():
    pa = pyaudio.PyAudio()
    lis = voiceai.listener.Listener(pa)
    audio = asyncio.run(lis.run())
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tp:
        wav = wave.open(tp, "wb")
        wav.setnchannels(voiceai.listener.CHANNELS)
        wav.setsampwidth(pyaudio.get_sample_size(voiceai.listener.FORMAT))
        wav.setframerate(voiceai.listener.RATE)
        wav.writeframes(audio)
        wav.close()
        print(f"wave file written to {tp.name}")

if __name__ == "__main__":
    main()
