from openai import AsyncOpenAI


class OpenAILLM:
    def __init__(self,  api_key: str, model="gpt-4o-mini", system_message=None):
        self.__client = AsyncOpenAI(api_key=api_key)
        self.__model = model
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

    async def chat_autocomplete(self, user_message: str) -> str:
        message = OpenAILLM.__create_user_message(user_message)
        self.__messages.append(message)
        completion = await self.__client.chat.completions.create(
            model=self.__model,
            messages=self.__messages,
        )
        response = completion.choices[0].message
        self.__messages.append(response)
        return response.content
    
    
