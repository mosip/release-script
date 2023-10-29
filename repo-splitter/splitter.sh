#!/bin/bash
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

# Specify the list of files and folders to preserve
FILES_TO_MOVE=(
  ".github"
  "db_scripts"
  ".gitignore"
  "pom.xml"
  "README.md"
  "LICENSE"
  "kernel/kernel-otpmanager-service"
)

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
$PIP_CMD install filter-repo

# Extract the repository name from the existing repository URL

REPO_NAME=$(basename "$EXISTING_REPO_URL" .git)

echo "Cloning " "$REPO_NAME" 
# Clone the existing repository and change to the repository directory
git clone "$EXISTING_REPO_URL"
cd "$REPO_NAME"

# Create a list of paths to preserve based on the OR condition
echo "setting up preserved path"
PRESERVE_PATHS=()
for item in "${FILES_TO_MOVE[@]}"; do
  PRESERVE_PATHS+=("--path" "$item")
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
