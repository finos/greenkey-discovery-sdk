# GreenKey Scribe Discovery SDK

The Discovery SDK allows you to write logic-based interpreters, and let Scribe's Discovery engine use probabalistic search to identify intents and entities.

You can use your Discovery interpreter to power several voice-driven workflows such as:

- Building a skill in combination with [Scribe's Real-Time Dictation](https://transcription.greenkeytech.com/sqc-06437d7/)

- Searching transcribed files for key phrases with [Scribe's File Transcription](https://transcription.greenkeytech.com/svt-e0286da/)

Read more about Discovery on our [blog](https://www.greenkeytech.com/news/2018/07/17/greenkey-scribe-discovery-skills/) or [checkout the full documentation](https://transcription.greenkeytech.com/discovery-1890af/)

### Repository overview
Each example contains a folder labeled `custom`, which in turn contains the needed `intents.json` and `entities` folder for launching Discovery.
Some examples contain a `schemas.json` file to customize the return json.
They also contain example scripts to see how the particular configuration will detect entities.

Feel free to use these examples as a jumping off point in your own code.

### Requirements

Docker 17+  
python  
python requests library (`pip install requests`)  


### Obtaining credentials
[Contact Us](mailto:transcription@greenkeytech.com) to obtain credentials to obtain the Discovery Docker container from our repository and launch the Discovery engine.

### Building your own interpreter

1) Copy an example folder or make one with the same structure

2) Create test cases in tests.txt with the following format:

```
test: {name of test}
transcript: {transcript you want to parse}
{entity 1}: {value}
{entity 2}: {value}
...
```

Ensure that your *transcripts are unformatted text with numbers spelled out*. Formatting will be taken care of by your entities, and the output from transcription engines will be unformatted.

3) Create your `intents.json` file to specify examples that resemble your tests.

4) Create any additional entities required by your intents.

5) Edit the credentials and other configuration parameters in `discovery_config.py`

6) Run `python test_discovery.py folder_name` to test your interpreter

### Testing with real audio

Scribe Discovery can work off of output from our delayed file transcription engine (SVTServer) or our real-time dictation engine (SQCServer).

For development purposes, it's easiest to first record a few audio files using your favorite software wherein you or someone else is speaking the voice commands or key phrases you want to interpret. Then, run these files through SVTServer [following our documentation](https://transcription.greenkeytech.com/svt-e0286da/) with the SVTServer parameter `WORD_CONFUSIONS="True"` enabled when you launch the container. Once complete, you should have a JSON file for each audio file you generated. This JSON file contains the **word confusion lattice** that Discovery searches for your target phrases.

These JSON files can be used directly with the Discovery Engine as [shown here](https://transcription.greenkeytech.com/discovery-1890af/deploying/#getting-started). The example directories provide guidance on how to send these files to discovery in the `send_transcript_to_discovery.sh`.
