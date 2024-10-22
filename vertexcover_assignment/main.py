import asyncio
import os
import tempfile
import time
import json

import pyaudio
import voiceai.listener
import voiceai.stt
import voiceai.llm


def main():
    pa = pyaudio.PyAudio()
    deepgram_key = os.getenv("DEEPGRAM_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    lis = voiceai.listener.Listener(pa)
    tts = voiceai.stt.DeepGramSTT(deepgram_key)
    llm = voiceai.llm.OpenAILLM(openai_key)

    async def main_loop():
        print("listening")
        audio = await lis.run()
        print("Audio obtained")

        print("sending to deepgram")
        start_time = time.perf_counter()
        message = tts.convert(audio)
        print(
            f"obtained response from deepgram in, {time.perf_counter() - start_time} seconds"
        )
        print(f"User said: {message}")

        print("sending to OpenAI for chat completion")
        start_tiem = time.perf_counter()
        response = await llm.chat_autocomplete(message)
        print(
            f"obtained response from OpenAI in, {time.perf_counter() - start_tiem} seconds"
        )
        print(f"Assitant says: {json.dumps(response)}")

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tp:
            tp.write(audio)
            print(f"wave file written to {tp.name}")
    asyncio.run(main_loop())


if __name__ == "__main__":
    main()
