import asyncio
import os
import tempfile
import time
import json

import pyaudio
from voiceai import VoiceAI


def main():
    deepgram_key = os.getenv('DEEPGRAM_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    voiceai = VoiceAI(deepgram_key, openai_key)
    asyncio.run(voiceai.run())


if __name__ == "__main__":
    main()
