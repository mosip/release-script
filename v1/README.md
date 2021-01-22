# Release script v1

## Requirements
* Linux (tested on Ubuntu > 18)
* Python version >= 3.6.9
* Java = {MOSIP Java version}
* Apache Maven > 3.6.0

## How to setup & run
* Download dependencies: `pip3 install -r requirements.txt`
* Create a .env inside v1 folder and copy the contents of .env.example file to .env file. Update the properties according. For more info, check [configuration parameters](./docs/configuration.md)
* Create or update inputData/repoList.json. It contains a list of repository urls. For example:

```text
[
  "https://github.com/mosip/durian.git",
  "https://github.com/mosip/pre-registration.git"
]
```
* Run script: `python3 main.py all`

## How to customize
You can find more info on customization and migration stages in [developer docs](./docs/developer.md)
