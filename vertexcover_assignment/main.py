import asyncio
import sys
import os

from voiceai import VoiceAI
from dotenv import load_dotenv

def main():
    deepgram_key = os.getenv('DEEPGRAM_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    if deepgram_key == "" or deepgram_key == "your-datagram-key-here":
        print("Deepgram API key not found")
        sys.exit(-1)
    if openai_key == "" or openai_key == "your-openai-key-here":
        print("OpenAI API Key not found")
        sys.exit(-1)

    voiceai = VoiceAI(deepgram_key, openai_key, enable_logs=True)
    asyncio.run(voiceai.run())

if __name__ == "__main__":
    load_dotenv()
    main()
