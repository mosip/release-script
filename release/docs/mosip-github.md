# Check the existence of a specific branch from all GitHub repositories of a GitHub account

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

* Get all repos present in account via `gh repo list <org>`.
* Check existence of specific branch in remote repo via `git ls-remote --heads git@github.com:<account>.git <branch>`
  ```
  $ repoList=$(gh repo list mosip | awk '/mosip/{print $1}' )
  $ for i in $repoList; do echo $i; git ls-remote --heads git@github.com:$i.git 1.2.0.2; done
  ```

# References

* [cli.github.com](https://cli.github.com/)