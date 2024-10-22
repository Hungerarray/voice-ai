# Voice AI

- [Voice AI](#voice-ai)
  - [Prerequisites](#prerequisites)
  - [Preparing dependency](#preparing-dependency)
  - [Running the application](#running-the-application)
  - [Potential shortcomings to improve](#potential-shortcomings-to-improve)


The following repository contains implementaion of Voice AI. An AI chatbot, that is integrated with DeepGram for Speech To Text (STT), OpenAI as chat bot assistant (LLM), and using the `tts-1` model from OpenAI as a Text To Speech (TTS) agent.

## Prerequisites
 - Python (used v3.12)
 - Poetry (for dependency management)
 
## Preparing dependency

If you have poetry installed, you can simply run,
```bash
$ poetry install
```

If you prefer using `requirements.txt` file and configuring your own `venv`. A `requirements.txt` is also provided.

## Running the application 

Once the dependencies have been installed, you can run either with
```bash
$ poetry run python vertexcover_assignment/main.py
```
or 
```bash
$ poetry shell
$ python vertexcover_assignment/main.py
```

In case you have not used poetry to install dependency, you just need to activate your `venv` then run the `main.py` file inside `vertexcover_assignment` directory.

## Potential shortcomings to improve 

- A way to skip conversations when AI starts speaking for a long time
