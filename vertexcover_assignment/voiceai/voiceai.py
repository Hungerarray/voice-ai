import pyaudio
import time
from .stt import DeepGramSTT
from .listener import Listener
from .llm import OpenAILLM


class VoiceAI:
    def __init__(self, deepgram_key: str, openai_key: str, enable_logs: bool = False):
        self.__pa = pyaudio.PyAudio()
        self.__listener = Listener(self.__pa, enable_log=enable_logs)
        self.__tts = DeepGramSTT(deepgram_key)
        self.__llm = OpenAILLM(openai_key, self.__pa, system_message="You are a conversational AI chat bot. Please keep your messages succinct and enable people well in converstaions.")
        self.__enable_logs = enable_logs

    async def run(self):
        message = 'Hello, I am your assistant. To exit say "goodbye"'
        print("====================")
        print(message)
        print("====================")
        self.__llm.speak(message)

        while True:
            print("\n\n")
            audio = await self.__listener.listen()
            
            audio_received_time = time.perf_counter()
            
            if self.__enable_logs:
                print("Processing ...")

            tts_convert_start_time = time.perf_counter()
            message = self.__tts.convert(audio)
            tts_convert_end_time = time.perf_counter()
            
            if self.__enable_logs:
                print("====================")
                print(f"User says: {message}")
            

            llm_response_start_time = time.perf_counter()
            response = self.__llm.chat_autocomplete(message)
            llm_response_end_time = time.perf_counter()
            
            if self.__enable_logs:
                print(f"Assitant says: {response}")
                print("====================")
            

            llm_speak_start_time = time.perf_counter()
            time_to_first_byte = self.__llm.speak(response)
            total_time_taken = time.perf_counter()

            if self.__enable_logs:
                print("====================")
                print("Stats")
                print(f"Time for STT conversion: {tts_convert_end_time - tts_convert_start_time} seconds")
                print(f"Time for llm response: {llm_response_end_time - llm_response_start_time} seconds")
                print(f"Time for TTS first byte: {time_to_first_byte - llm_speak_start_time} seconds")
                print(f"Time to TTS first byte since user silent: {time_to_first_byte - audio_received_time} seconds")
                print(f"Total conversation Time: {total_time_taken - audio_received_time} seconds")
                print("====================")
            
            # check if goodbye is the final word in the sentence
            if 'goodbye' in message.lower().split()[-1]:
                break
