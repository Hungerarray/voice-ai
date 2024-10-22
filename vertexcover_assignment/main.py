import asyncio
import json
import sys
import os
import tempfile
import time

import pyaudio

from voiceai import VoiceAI

def main():
    deepgram_key = os.getenv('DEEPGRAM_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    if deepgram_key == "":
        print("Deepgram API key not found")
        sys.exit(-1)
    if openai_key == "":
        print("OpenAI API Key not found")
        sys.exit(-1)

    voiceai = VoiceAI(deepgram_key, openai_key, enable_logs=True)
    asyncio.run(voiceai.run())

if __name__ == "__main__":
    main()
