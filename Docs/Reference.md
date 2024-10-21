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
 

