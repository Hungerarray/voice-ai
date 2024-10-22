# Audio Files

- [Audio Files](#audio-files)
  - [How Audio files are recreated](#how-audio-files-are-recreated)
  - [Terms](#terms)
- [PyAudio](#pyaudio)
  - [PreRequisites](#prerequisites)
- [WebRTCVAD](#webrtcvad)
  - [Prerequisites](#prerequisites-1)
- [DeepGram](#deepgram)
  - [Models](#models)
    - [Languages supported](#languages-supported)
  - [API Rate limits](#api-rate-limits)
  - [Cost Economics](#cost-economics)
  - [Alternatives](#alternatives)
  - [Additional Considerations](#additional-considerations)
- [OpenAI](#openai)
  - [Models](#models-1)
  - [Pricing](#pricing)
  - [Rate Limits](#rate-limits)
  - [Alternatives](#alternatives-1)
  - [Additional Considerations](#additional-considerations-1)


## How Audio files are recreated

We are let with a series of positive and negative voltages, that with properties such as amplitude and frequency, are able to reproduce the sound they represent. Now we introduce an Analog to Digital converter, also known as an A-D converter. This is a device that takes digital snapshots of the analog signal at a defined rate, called a Sample Rate. The most common Sample Rates are 44.1kHz and 48kHz. Each snapshot it takes, it uses strings of binary information (1s and 0s) to represent the voltages in the analog audio.

Essentially, a camera takes a photo of the signals position 44,100 times every second (or up to 192,000 per second.) That "photo" contains bits that are represented by the 1s and 0s. The amount of bits can vary too, according to the Bit Depth. Bit Depth is usually 16 or 24, and all it means is how many bits are used to represent the position of the signal during every sample.

Simply put, using CD standard of a sample rate of 44.1kHz and a bit depth of 16, every second you have 44,100 samples represented by 16 bits each. That is the analog audio represented digitally

## Terms

- **Sampling Frequency or Sample Rate**: The number of times that the sound level is sampled per second. Typical value 44,000 per second or 44 KHz

- **Sample Resolution or Bit Depth**: The number of bits available for each sample. Typical values, 16 bits on CD and 24 Bits on DVD.

- **Bit rate**: The number of bits used per second of audio. Calculated using, 
$\text{sample frequency} * \text{bit depth}$

- **File Size**: Calculated using,
$\text{File Size} = \text{Sample Rate} * \text{Sample Resolution} * \text{Length of sound} = \text{Bit Rate} * \text{Length of Sound}$

- **Audio Channel**: Defined as the representation of sound coming from or going to a single point. An audio file mixed for headphones will use 2 channels, while the ones mixed for movie production will have 6 different audio channels. A regular setup will have a single mic, which means you can only have 1 audio input channel. While, it is possible to generate 2 channel audio, by using software, careful considerations might be needed.

# PyAudio

## PreRequisites
 - portaudio
 
For streaming in a non-blocking manner, it is essential to use in [callback mode](https://people.csail.mit.edu/hubert/pyaudio/docs/#example-callback-mode-audio-i-o).

Parameters to open PyAudio Stream,
- format = the same as bit depth, (Default, paInt16 = 16 bit depth, good enough for music)
- rate = Sampling rate, depends on what DeepGram is capable of processing
- channels = 1 (assume single mic)
- input = True, we need input stream channel
- frames_per_buffer = A single frame is format * channels bytes large, this specifies how many frames we wish to have per buffer, aka, chunk.
- stream_callback = callback that is called for each chunk. If this is set, do not use `read` or `write` operation.

# WebRTCVAD

Voice Audio Detection, by Google. It's claimed to have the best performance in the block.

## Prerequisites
    - 16 bit (paInt16 should work)
    - Mono audio (there should be only 1 channel, currently we use only 1 channel)
    - Sample rate of, 8KHz, 16KHz, 32KHz, or 48KHz (we will use 16KHz)
    - Frames must be 10, 20, or 30ms in duration
    
We compute the chunk size. Considering that our frames will be of 30ms in size. In 1 second we have 16000 frames, so in 30 ms we will have, 16000 * 30 / 1000 = 480 Frames.
Similarly, our strategy will be to look at the past 2 seconds of data. If 50% of them are marked as voiced, we start collecting them into a voiced bucket. Again, if we have more than 2 seconds of no speech while gathering then we will stop collecting and send all in the voiced bucket to inference engine.
Since there are chunks every 30ms, there will be about 2000 / 30 chunks = 66.67 = 67 chunks.
So our ring buffer will have maxlen of 67 chunks.

[Example reference](https://github.com/wiseman/py-webrtcvad/blob/master/example.py)

# DeepGram

To use DeepGram we need to adhere to few media specifications as highlighted [here](https://developers.deepgram.com/docs/tts-media-output-settings#audio-format-combinations).

The major points, we will be using Streaming API with WebSockets, that only supports 3 formats. Out of which with PyAudio we are using `linear16` Encoding scheme. This scheme only supports Sample rate of `8000`, `16000`, `24000`, `32000`, and `48000` Hz.

After multiple tests, and various references, `16000` seems to be the best sample rate for audio. Any other sample rate doesn't yield as good of response.

After more tests, sending wav file yielded much better response than what live streaming was capable of. 

For STT, we will use PyAudio to record sound, then use a VAD to find if speech is being generated. If there is no speech detected for some time then, we will transfer this file to DeepGram to generate response.

## Models

While there are multiple models to choose from, we will be using only `nova-2`.  `nova-2` also various model options to choose from,
 - `general`
 - `meeting`
 - `phonecall`
 - `voicemail`
 - `finance`
 - `conversationalai` 
 - `video`
 - `medical`
 - `drivethru`
 - `automotive`
 - `atc`

For the sake of assignment we will use, `conversationalai` version. Further details can be found [here](https://developers.deepgram.com/docs/model#nova-2)

### Languages supported

Only `nova-2-general` supports multiple languages. Other enhanced model only support `en-US`.

## API Rate limits
This is for "Pay As You Go" `nova-2` model.
- 100 Concurrent requests

## Cost Economics

At "Pay As You Go" model with `nova-2`, expected cost is, `$0.0043/min`.

## Alternatives

Self hosting `Whisper-large` instance.

## Additional Considerations

They also provide Text-To-Speech API. For this they have only 1 model `Aura`. The pricing is `$0.0150/1k` characters. The API limits for this model are,
    - 2000 Maximum Characters
    - 480 Requests Per minute
    - 2 concurrent requests


# OpenAI

It has a simple REST API to send all the user messages. However, we also need to append `system message` along with it. Once we do recieve the answer, we need to send it back to OpenAI to generate TTS that can be played. It would be better to store this TTS as wav file temporarily in system somewhere. Since it will be a CLI application, we will only show the texts received and play them out together, with no possibility of replay.

## Models
We have the options of using GPT-3.5 or GPT-4o-mini. GPT 4o mini is considered to have better performance while being cheaper. So we pick GPT 4o mini instead.

## Pricing

| Model         | Pricing                |
| ------------- | ---------------------- |
| GPT 3.5 Turbo | $3/1M input tokens     |
| GPT 4o mini   | $0.150/1M input tokens |
| GPT 40        | $2.5/1M input tokens   |

Further details are available [here](https://openai.com/api/pricing/).

## Rate Limits

Rate limits in OpenAI depend on your usage tier. For Free tier you have,


| Model         | Requests Per Minute | Requests Per Day | Tokens Per Minute |
| ------------- | ------------------- | ---------------- | ----------------- |
| gpt-3.5-turbo | 3                   | 200              | 40,000            |
| tts-1         | 3                   | 200              | -                 |

The usage of API is not free, and is only possible if you have free credits provided by OpenAI which seems to have been stopped.

For user who has spent $5, they are upgraded to tier 1 and have following limits,

| Model         | Requests Per Minute | Requests Per Day | Tokens Per Minute |
| ------------- | ------------------- | ---------------- | ----------------- |
| gpt-4o        | 500                 | -                | 30,000            |
| gpt-4o-mini   | 500                 | 10,000           | 200,000           |
| gpt-3.5-turbo | 3,500               | 10,000           | 200,000           |
| tts-1         | 500                 | -                | -                 |
| tts-1-hd      | 500                 | -                | -                 |

Further details can be found [here](https://platform.openai.com/docs/guides/rate-limits/tier-1-rate-limits).

## Alternatives

Self hosting open source llm, lama is possible using [ollama](https://ollama.com/). For TTS, we can use Deepgram. There are some other [suggestions](https://docs.google.com/document/d/1sariO32u4a87vfZDzAR-fq2RwuZ_zxBj29vMG8UFH2s/edit?tab=t.0#heading=h.y2rv92en8xpt), but require further digging.

## Additional Considerations

While for the current simple execution purposes we make use of OpenAI API using it's official SDK. For any complex application, the use of LangChain would be preferable.