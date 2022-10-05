# GitHub Utilities
* Find below all the necessary GitHub utils for repositories monitoring and control.

## Prerequisite

* Install `gh` package. Follow the instruction from [here](https://github.com/cli/cli/blob/trunk/docs/install_linux.md#debian-ubuntu-linux-raspberry-pi-os-apt).
* Login with your account token.
  ```
  username@hostname:~$ gh auth login
  ? What account do you want to log into? GitHub.com
  ? What is your preferred protocol for Git operations? HTTPS
  ? Authenticate Git with your GitHub credentials? Yes
  ? How would you like to authenticate GitHub CLI? Paste an authentication token
  Tip: you can generate a Personal Access Token here https://github.com/settings/tokens
  The minimum required scopes are 'repo', 'read:org', 'workflow'.
  ? Paste your authentication token: xxxxxxxxxxxxxxxxxxxxxxxxxx
  - gh config set -h github.com git_protocol https
    ✓ Configured git protocol
    ✓ Logged in as xxxxxxxx
  ```

## Utils

* Get all repos present in account via `gh repo list <org>`.

* Check the existence of a specific branch from all GitHub repositories of a GitHub account
    * Check existence of specific branch in remote repo via `git ls-remote --heads git@github.com:<account>.git <branch>`
      ```
      $ repoList=$(gh repo list mosip | awk '/mosip/{print $1}' )
      $ for i in $repoList; do echo $i; git ls-remote --heads git@github.com:$i.git 1.2.0.2; done
      ```

* Filter PRs
    * Filter prs based on organisation `ORG`, base branch `release-1.2.0.1` & merged start date `>=2022-02-01` & file type `.sql`
      ```
      PR_BASE_BRANCH=release-1.2.0.1
      MERGED_START_DATE='>=2022-02-01'
      FILE_TYPE=".sql"
      ORG="mosip"
      
      repoList=$(gh repo list $ORG | awk '/'$ORG'/{print $1}' );
      for repo in $repoList; do
        #echo "REPO : $repo"
        PRID=$(gh search prs --repo $repo --merged --base "$PR_BASE_BRANCH" --merged-at "$MERGED_START_DATE" --json 'number' --jq '.[].number' 2>&1);
        sleep 2;
        for pr in $PRID; do
          SQL_COUNT=$( gh pr view --repo $repo $pr --json files --jq ".files.[] | select (.path|match(\"$FILE_TYPE\")) |.path" | wc -l 2>&1)
          if [ $SQL_COUNT -gt 0 ]; then
            echo "https://github.com/$repo/pull/$pr/files";
          fi
        done
      done
      ```

## References

* [cli.github.com](https://cli.github.com/)
