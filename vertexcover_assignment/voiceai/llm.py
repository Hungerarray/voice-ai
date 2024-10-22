from openai import OpenAI
import time
import pyaudio


class OpenAILLM:
    def __init__(self,  api_key: str, pa: pyaudio.PyAudio, chat_model="gpt-4o-mini", audio_model="tts-1", audio_voice='alloy', system_message=None):
        self.__client = OpenAI(api_key=api_key)
        self.__pa = pa
        self.__chat_model = chat_model
        self.__audio_model = audio_model
        self.__audio_voice = audio_voice
        self.__messages = []
        if system_message is not None:
            self.__messages.append(OpenAILLM.__create_system_message(system_message))

    @staticmethod
    def __create_message(role: str, message: str):
        return {"role": role, "content": message}

    @staticmethod
    def __create_system_message(message: str):
        return OpenAILLM.__create_message("system", message)

    @staticmethod
    def __create_user_message(message: str):
        return OpenAILLM.__create_message("user", message)

    def chat_autocomplete(self, user_message: str) -> str:
        message = OpenAILLM.__create_user_message(user_message)
        self.__messages.append(message)
        completion = self.__client.chat.completions.create(
            model=self.__chat_model,
            messages=self.__messages,
        )
        response = completion.choices[0].message
        self.__messages.append(response)
        return response.content

    def speak(self, message: str):
        # these values are obtaied from reference example in official OpenAI Python SDK
        speaker_stream = self.__pa.open(format=pyaudio.paInt16, channels=1, rate=24000, output=True)
        start_time = time.perf_counter()
        with self.__client.audio.speech.with_streaming_response.create(
            model=self.__audio_model,
            voice=self.__audio_voice,
            response_format='pcm',
            input=message
        ) as response:
           print(f"Time to first byte: {time.perf_counter() - start_time} seconds") 
           for chunk in response.iter_bytes(chunk_size=1024):
               speaker_stream.write(chunk)
        print(f"Done in {time.perf_counter() - start_time} seconds")

    
