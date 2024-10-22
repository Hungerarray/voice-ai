import asyncio
import collections
import io
import wave
import webrtcvad
from enum import Enum
import math
import pyaudio


# !Warning
# These constants were determined after various testing phase
# as such are known combination to work. 
# While they can be exposed to user, changing them could lead to
# noticable degradation of quality
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
# A chunk is the number of frames in a buffer, if we want 30ms duration frames,
# Chunk size =  (0.03 * RATE) Frames
MS_IN_SEC = 1000
VAD_FRAME_MS = 30
VAD_WINDOW_S = 1
VAD_ACTIVATION_RATE = 0.5

CHUNK = math.ceil(VAD_FRAME_MS / MS_IN_SEC * RATE)
VAD_BUFF_MAX_LEN = math.ceil(VAD_WINDOW_S * MS_IN_SEC / VAD_FRAME_MS)


class SpeechState(Enum):
    NOT_SPEAKING = 2
    SPEAKING = 1

class Listener():
    def __init__(self, pa: pyaudio.PyAudio, enable_log: bool = False):
        self.__pa = pa
        self. __audio_queue = asyncio.Queue()
        self.__stream = None
        self.__enable_log = enable_log

    # each time this get's called I want to store it in some wave file at temporary location

    def __start_microphone(self, loop: asyncio.AbstractEventLoop) -> None:
        # if we are running in a loop, we probably want to move it outside
        def mic_callback(input_data, frame_count, time_info, status_flag):
            # this had to be done as we are using asyncio Queue, that is not thread safe
            # so we schedule it to called on the running loop thread eventually for other
            # functionalities to work
            loop.call_soon_threadsafe(self. __audio_queue.put_nowait, input_data)
            # since our stream has no output, we can send None
            return (None, pyaudio.paContinue)

        self.__stream = self.__pa.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
            stream_callback=mic_callback,
        )

    def __stop_microphone(self) -> None:
        if self.__stream is None:
            return

        self.__stream.stop_stream()
        self.__stream.close()

    async def __mic_listen(self) -> bytes:
        all_mic_data = []
        speech_state = SpeechState.NOT_SPEAKING
        vad_buff = collections.deque(maxlen=VAD_BUFF_MAX_LEN)
        vad = webrtcvad.Vad()
        once = True
        # VAD code must be set here
        # Initially we are in not speaking state
        if self.__enable_log:
            print("====================")
            print("Listening...")
        while True:
            mic_data = await self. __audio_queue.get()
            is_speech = vad.is_speech(mic_data, RATE)

            # we don't start "Listening" until we have confirmed 50% or more of voiced frames in past 1 second
            if speech_state == SpeechState.NOT_SPEAKING:
                vad_buff.append((mic_data, is_speech))
                num_voiced = sum([1 for _, speech in vad_buff if speech])
                if num_voiced >= VAD_ACTIVATION_RATE * VAD_BUFF_MAX_LEN:
                    speech_state = SpeechState.SPEAKING
                    for f, _ in vad_buff:
                        all_mic_data.append(f)
                    vad_buff.clear()
            # We stop "Listening" when we have had 50% or more unvoiced frames in past 1 second
            elif speech_state == SpeechState.SPEAKING:
                if self.__enable_log and once:
                    print("User is now speaking")
                    once = False
                all_mic_data.append(mic_data)
                vad_buff.append((mic_data, is_speech))
                num_unvoiced = sum([1 for _, speech in vad_buff if not speech])
                if num_unvoiced >= VAD_ACTIVATION_RATE * VAD_BUFF_MAX_LEN:
                    break

            self. __audio_queue.task_done()

        self.__stop_microphone()

        # We terminate the "Listening" phase and discard any data after
        while not self. __audio_queue.empty():
            self. __audio_queue.get_nowait()
            self. __audio_queue.task_done()

        # we do this, as we need the various wav header information 
        # for details like #channels, sample_rate, etc.
        frames = b"".join(all_mic_data)
        buffer = io.BytesIO()
        wav = wave.open(buffer, 'wb')
        wav.setnchannels(CHANNELS)
        wav.setsampwidth(pyaudio.get_sample_size(FORMAT))
        wav.setframerate(RATE)
        wav.writeframes(frames)
        wav.close()
        buffer.seek(0)
        return buffer.read()

    async def listen(self) -> bytes:
        loop = asyncio.get_running_loop()
        self.__start_microphone(loop)
        audio = await self.__mic_listen()
        return audio
