# Release script v1

## Objectives
* Verifies the repo to be release contains the respective release branch
* Verifies whether the branch contains any old dependency
* Remove need of manually updating pom version that may cause human error
* Checks whether the modules in repo are building successfully
* Updates the release url

## Requirements
* Linux (tested on Ubuntu > 18)
* Python version >= 3.9
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
* Run script:
```text
$python can be python3, python3.9, py etc

For dry run: $python main.py all
For non-release: $python main.py all --prod
For release: $python main.py all --release --prod

--prod: it will make version updates to te pom.xml files
--release: will update the push trigger and release url
```

## How to customize
You can find more info on customization and migration stages in [developer docs](./docs/developer.md)
