import pyaudio
from .stt import DeepGramSTT
from .listener import Listener
from .llm import OpenAILLM


class VoiceAI:
    def __init__(self, deepgram_key: str, openai_key: str):
        self.__pa = pyaudio.PyAudio()
        self.__listener = Listener(self.__pa)
        self.__tts = DeepGramSTT(deepgram_key)
        self.__llm = OpenAILLM(openai_key, self.__pa)

    async def run(self):
        while True:
            audio = await self.__listener.listen()
            message = self.__tts.convert(audio)
            response = self.__llm.chat_autocomplete(message)
            self.__llm.speak(response)
            
            if 'goodbye' in message.lower():
                break
