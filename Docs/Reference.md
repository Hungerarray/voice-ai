# Audio Files

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

## PyAudio

### PreRequisites
 - portaudio
 
For streaming in a non-blocking manner, it is essential to use in [callback mode](https://people.csail.mit.edu/hubert/pyaudio/docs/#example-callback-mode-audio-i-o).

Parameters to open PyAudio Stream,
- format = the same as bit depth, (Default, paInt16 = 16 bit depth, good enough for music)
- rate = Sampling rate, depends on what DeepGram is capable of processing
- channels = 1 (assume single mic)
- input = True, we need input stream channel
- frames_per_buffer = A single frame is format * channels bytes large, this specifies how many frames we wish to have per buffer, aka, chunk.
- stream_callback = callback that is called for each chunk. If this is set, do not use `read` or `write` operation.

## WebRTCVAD

Voice Audio Detection, by Google. It's claimed to have the best performance in the block.

### Prerequisites
    - 16 bit (paInt16 should work)
    - Mono audio (there should be only 1 channel, currently we use only 1 channel)
    - Sample rate of, 8KHz, 16KHz, 32KHz, or 48KHz (we will use 16KHz)
    - Frames must be 10, 20, or 30ms in duration
    
We compute the chunk size. Considering that our frames will be of 30ms in size. In 1 second we have 16000 frames, so in 30 ms we will have, 16000 * 30 / 1000 = 480 Frames.
Similarly, our strategy will be to look at the past 2 seconds of data. If 50% of them are marked as voiced, we start collecting them into a voiced bucket. Again, if we have more than 2 seconds of no speech while gathering then we will stop collecting and send all in the voiced bucket to inference engine.
Since there are chunks every 30ms, there will be about 2000 / 30 chunks = 66.67 = 67 chunks.
So our ring buffer will have maxlen of 67 chunks.

[Example reference](https://github.com/wiseman/py-webrtcvad/blob/master/example.py)

## DeepGram

To use DeepGram we need to adhere to few media specifications as highlighted [here](https://developers.deepgram.com/docs/tts-media-output-settings#audio-format-combinations).

The major points, we will be using Streaming API with WebSockets, that only supports 3 formats. Out of which with PyAudio we are using `linear16` Encoding scheme. This scheme only supports Sample rate of `8000`, `16000`, `24000`, `32000`, and `48000` Hz.

After multiple tests, and various references, `16000` seems to be the best sample rate for audio. Any other sample rate doesn't yield as good of response.

After more tests, sending wav file yielded much better response than what live streaming was capable of. 

For STT, we will use PyAudio to record sound, then use a VAD to find if speech is being generated. If there is no speech detected for 3 or 4 seconds, we will then compress the wav file to only include speech sections, and then transfer this file to DeepGram to generate response.

## OpenAI

It has a simple REST API to send all the user messages. However, we also need to append `system message` along with it. Once we do recieve the answer, we need to send it back to OpenAI to generate TTS that can be played. It would be better to store this TTS as wav file temporarily in system somewhere. Since it will be a CLI application, we will only show the texts received and play them out together, with no possibility of replay.

