from deepgram import DeepgramClient, PrerecordedOptions, FileSource


class DeepGramSTT:
    def __init__(self, api_key: str):
        self.__deepgram = DeepgramClient(api_key=api_key)
        self.__options = PrerecordedOptions(
            model="nova-2-conversationalai",
            smart_format=True,
        )

    def convert(self, buffer: bytes) -> str:
        payload: FileSource = {"buffer": buffer}
        response = self.__deepgram.listen.prerecorded.v('1').transcribe_file(payload, self.__options)

        # we have only 1 channel
        channels = response.results.channels
        # we only take the first transcript,
        # in our case we have 1 channel, so the first must always be true
        if len(channels) >= 1 and len(channels[0].alternatives) >= 1:
            transcript = channels[0].alternatives[0].transcript
        else:
            transcript = ''
        return transcript
