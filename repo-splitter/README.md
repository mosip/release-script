# Repository Splitting Script

## Usage

1. Create a `repo.properties` file in the same directory as the script with the following properties:

   - `EXISTING_REPO_URL`: The URL of the existing Git repository that you want to split.
   - `NEW_REPO_URL`: The URL of the new Git repository that will be created.
   - `FILES_TO_MOVE`: A space-separated list of files and folders that you want to preserve when splitting the repository.

   Example `repo.properties` file:
   ```properties
   EXISTING_REPO_URL=https://github.com/username/repo.git
   NEW_REPO_URL=https://github.com/username/new-repo.git
   FILES_TO_MOVE=".github db_scripts .gitignore pom.xml README.md LICENSE"
1. Run the script:
   ```./repository-split.sh```
## Configuration Details
* EXISTING_REPO_URL: This should be the URL of the Git repository you want to split. Make sure you have the necessary permissions to clone it.
* NEW_REPO_URL: Specify the URL for the new Git repository that will be created. Ensure that this repository is created and accessible.
* FILES_TO_MOVE: List the files and folders you want to preserve in the new repository, separated by spaces. These items will be retained during the splitting process.
## Precautions
* Ensure that the repo.properties file is correctly formatted, and the URLs are accurate.
* Be cautious when using this script, as it will alter repositories. Make sure you have backups or a way to restore your data if something goes wrong.
* Make sure you have permissions to clone and push to the repositories specified in EXISTING_REPO_URL and NEW_REPO_URL.
* Regularly review and update the repo.properties file to reflect any changes in the repository URLs or the list of files and folders to preserve.
* Test the script on a non-critical repository or create a copy for testing before using it on a production repository.
