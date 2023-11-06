#!/bin/bash

function repo_splitter() {
  exec 3>&1 4>&2
  trap 'exec 2>&4 1>&3' 0 1 2 3
  exec > >(tee -a log.out) 2>&1

# Load properties from repo.properties
  if [ -f "repo.properties" ]; then
      source "repo.properties"
  else
      echo "Error: repo.properties file not found."
      exit 1
  fi

# Extract the repository name from the existing repository URL
  REPO_NAME=$(basename "$EXISTING_REPO_URL" .git)

# Check if the directory with the name REPO_NAME exists
  if [ -d "$REPO_NAME" ]; then
      read -p $'\e[91mSource Repo already seems to be available at present location, Do you want to override? (y/n): \e[0m' ANSWER
      if [[ "$ANSWER" == "y" ]]; then
          # Delete current repo and re-clone
          rm -rf "$REPO_NAME"
          git clone "$EXISTING_REPO_URL"
      elif [[ "$ANSWER" == "n" ]]; then
          echo "Repo already exists in this diretory. Please perform the operation from a new directory."
          exit 1
      else
          echo "Invalid choice. Exiting."
          exit 1
      fi
  else
      # Directory doesn't exist, clone the repository
      git clone "$EXISTING_REPO_URL"
  fi

# Check if python3 is available
  if command -v python3 &> /dev/null; then
      PYTHON_CMD="python3"
      PIP_CMD="pip3"
  elif command -v python &> /dev/null; then
      PYTHON_CMD="python"
      PIP_CMD="pip"
  else
      # Install Python3
      echo "Python and Python3 are not installed. Installing Python3..."
      sudo apt update
      sudo apt install -y python3
      PYTHON_CMD="python3"
      PIP_CMD="pip3"
  fi
# Install filter-repo
  echo "Install filter-repo using " $PIP_CMD
  $PIP_CMD install git-filter-repo

  cd "$REPO_NAME"

  # Convert FILES_TO_MOVE into an array
  IFS=' ' read -r -a FILES_TO_MOVE <<< "$FILES_TO_MOVE"

# Create a list of paths to preserve based on the OR condition
  echo "setting up preserved path"
  PRESERVE_PATHS=()
  for item in "${FILES_TO_MOVE[@]}"; do
    PRESERVE_PATHS+=("--path")
    PRESERVE_PATHS+=("$item")
  done


# Use git filter-repo to create a filtered repository
  echo "Filtering the repo for mentioned services" "${PRESERVE_PATHS[@]}"
  git filter-repo "${PRESERVE_PATHS[@]}"

# Add the new repository as a remote
  echo "Adding new remote URL " "$NEW_REPO_URL"
  git remote add new-remote "$NEW_REPO_URL"

# Push all branches to the new repository
  echo "Pushing changes to " "$NEW_REPO_URL"
  git push new-remote --all

  echo "Repo Splitting activity completed"
  return 0
}

# set commands for error handling.
set -e
set -o errexit   ## set -e : exit the script if any statement returns a non-true return value
set -o nounset   ## set -u : exit the script if you try to use an uninitialised variable
set -o errtrace  # trace ERR through 'time command' and other functions
set -o pipefail  # trace ERR through pipes
repo_splitter    # calling function
