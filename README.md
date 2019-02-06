# GreenKey Scribe Discovery SDK [![Build Status](https://travis-ci.org/finos-voice/greenkey-discovery-sdk.svg?branch=master)](https://travis-ci.org/finos-voice/greenkey-discovery-sdk)
> Speed up business workflows through creating custom 'voice skills' and text interpreters

<img src="https://github.com/finos-voice/greenkey-voice-sdk/raw/master/logo/greenkey-logo.png" width="100" />

---

The Discovery SDK allows you to write logic-based interpreters, and let Scribe's Discovery engine use probabilistic search to identify intents and entities.

You can use your Discovery interpreter to power several voice-driven workflows such as:

- Building a skill in combination with [Scribe's Real-Time Dictation](https://transcription.greenkeytech.com/sqc-06437d7/)

- Searching transcribed files for key phrases with [Scribe's File Transcription](https://transcription.greenkeytech.com/svt-e0286da/)

Read more about Discovery on our [blog](https://www.greenkeytech.com/news/2018/07/17/greenkey-scribe-discovery-skills/) or [checkout the full documentation](https://transcription.greenkeytech.com/discovery-1890af/)

The GreenKey Discovery SDK
is hosted by the [Voice Program] of the Fintech Open Source Foundation ([FINOS]).
If you are a company interested in the evolution of
open standards, interoperability, and innovation in the financial services sector,
please consider joining FINOS.

### Repository overview
Each example contains a folder labeled `custom`, which in turn contains the needed `intents.json` and `entities` folder for launching Discovery.
Some examples contain a `schemas.json` file to customize the return json.
They also contain example scripts to see how the particular configuration will detect entities.

```
examples
└── room_number
    ├── custom
    │   ├── entities
    │   │   └── room_number.py
    │   └── intents.json
    ├── send_transcript_to_discovery.sh
    └── tests.txt
```

Feel free to use these examples as a jumping off point in your own code.

### Requirements

- Docker 17+ (or Discovery Binaries)
- Python 3 with `pip`

### Dependencies

To ensure your dependencies install correctly, we recommend that you upgrade your `setuptools` before proceeding further.

```sh
python3 -m pip install --upgrade setuptools
```

Now you are ready to install the required dependencies with `pip`.
This will provide you with the packages needed to run the `test_discovery.py` script, as well as the Discovery CLI.

```sh
python3 -m pip install -r requirements.txt
```

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

6) Run `python3 test_discovery.py folder_name` to test your interpreter. For example:

```
python test_discovery.py examples/directions
```

### Using Compiled Binary Files

If you are unable to use Docker, contact us to obtain compiled binary files for Discovery.
Simply place the binaries directory into the SDK directory before running `test_discovery.py`.
The test script will automatically detect the binaries directory and use that instead of a Docker image.

Make sure not to change the name of the binaries file when you move it.
You should end up with a structure like the following for the `test_discovery.py` script to work.

```
└───greenkey-discovery-sdk
    └───discovery_binaries_windows_10_64bit__python37_64bit
    └───examples
    └───gkcli
    │   discovery_config.py
    │   README.md
    │   test_discovery.py
```

### Using the Discovery CLI tool

The Discovery CLI is a tool that can aid in the creation of custom definition files for use with Discovery.

#### Usage

Once the CLI is installed, it is invoked with the command `gk_cli`.

You can use the tool to either create a new project, or to create an individual entity.

Before invoking the tool, navigate to the directory where you wish to create your new file or files.
- If you wish to create an entire project, navigate to the directory that will hold your `custom` folder. If you have not made your `custom` folder, the CLI will guide you through the creation of one.
- If you have already created a project, and simply wish to create an entity, navigate to your `entities` folder before running the tool. If you have not made your `entities` folder in your project, the CLI will guide you through the creation of one.

If the installation was successful, you should see the following output after invoking the tool~
```sh
$ gk_cli

? What would you like to do?  (Use arrow keys)
 ❯ Create a new entity
   Create a new project
```

### Testing with real audio

Scribe Discovery can work off of output from our delayed file transcription engine (SVTServer) or our real-time dictation engine (SQCServer).

For development purposes, it's easiest to first record a few audio files using your favorite software wherein you or someone else is speaking the voice commands or key phrases you want to interpret.

Then, run these files through SVTServer [following our documentation](https://transcription.greenkeytech.com/svt-e0286da/) with the SVTServer parameter `WORD_CONFUSIONS="True"` enabled when you launch the container.

For example, you can launch a single job container with the following command for a file called `test.wav`. Be sure to set `$USERNAME` and `$SECRETKEY`

```bash
docker run \
    -it \
    --rm \
    --name svtserver-test \
    -e GKT_API="https://scribeapi.greenkeytech.com/" \
    -e GKT_USERNAME="$USERNAME" \
    -e GKT_SECRETKEY="$SECRETKEY" \
    -e TARGET_FILE="/files/test.wav" \
    -v "$PWD":/files \
    -e ENABLE_CLOUD="False" \
    -e PROCS=1 \
    docker.greenkeytech.com/svtserver
```

Once complete, you should have a JSON file for each audio file you generated. This JSON file contains the **word confusion lattice** that Discovery searches for your target phrases.

These JSON files can be used directly with the Discovery Engine as [shown here](https://transcription.greenkeytech.com/discovery-1890af/deploying/#getting-started). The example directories provide guidance on how to send these files to discovery in the `send_transcript_to_discovery.sh`.

## Contributing

### Code of Conduct

Please make sure you read and observe our [Code of Conduct].

### Pull Request process

1. Fork it
1. Create your feature branch (`git checkout -b feature/fooBar`)
1. Commit your changes (`git commit -am 'Add some fooBar'`)
1. Push to the branch (`git push origin feature/fooBar`)
1. Create a new Pull Request

## Versioning

We use [SemVer] for versioning.  For the versions available, see the [tags on this repository].

## Authors

Original authors:

- [Ashley Shultz](https://github.com/AGiantSquid)
- [Matthew Goldey](https://github.com/mgoldey)
- [Tejas Shastry](https://github.com/tshastry)

For all others who have aided this project, please see the [list of contributors].

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE.md](LICENSE.md) file for details.

<!-- Markdown link & img defs -->
[FINOS]: https://www.finos.org
[Code of Conduct]: https://www.finos.org/code-of-conduct
[Voice Program]: https://finosfoundation.atlassian.net/wiki/spaces/VOICE/overview
[SemVer]: http://semver.org
[list of contributors]: https://github.com/finos-voice/greenkey-discovery-sdk/graphs/contributors
[tags on this repository]: https://github.com/finos-voice/greenkey-discovery-sdk/tags
