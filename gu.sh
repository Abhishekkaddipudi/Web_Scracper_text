#!/bin/bash

# STEP 1: Download chapter_full.json using godown
#!/bin/bash

# Default value
auto_response=""

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -y|--yes)
            auto_response="yes"
            shift
            ;;
        -n|--no)
            auto_response="no"
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [-y|--yes] [-n|--no] [-h|--help]"
            echo "  -y, --yes    Skip confirmation prompt and download automatically"
            echo "  -n, --no     Skip confirmation prompt and skip download"
            echo "  -h, --help   Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

# Use the passed input or prompt user
if [ "$auto_response" = "yes" ]; then
    yn="y"
elif [ "$auto_response" = "no" ]; then
    yn="n"
else
    read -p "Do you want to download chapter_full.json using gdown? [Y/n]: " yn
fi

case "$yn" in
    [Yy]* | "" )
        echo "[$(date '+%Y-%m-%d %H:%M:%S %z')] [$$] [gdown]: Downloading"
        gdown --fuzzy "https://drive.google.com/file/d/1nPn5ICvdxqOcdK5XHWshp1qPCGVldG-p/view?usp=drivesdk"
        ;;
    [Nn]* )
        echo "[$(date '+%Y-%m-%d %H:%M:%S %z')] [$$] [gdown]: Skipping download"
        ;;
    * )
        echo "Invalid input. Skipping download."
        ;;
esac
# STEP 2: Git update in sub_portfolio/
cd Web_Scracper_text/sub_portfolio/
git fetch origin
Local=$(git rev-parse @)
remote=$(git rev-parse @{u})
base=$(git merge-base @ @{u})

if [ "$Local" = "$remote" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S %z')] [$$] [git]: Already up to date"
elif [ "$Local" = "$base" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S %z')] [$$] [git]: Changes detected! Pulling"
    git pull
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S %z')] [$$] [git]: Local and remote have diverged"
fi

# STEP 3: Git update in Web_Scracper_text/
cd ..
git fetch origin
Local=$(git rev-parse @)
remote=$(git rev-parse @{u})
base=$(git merge-base @ @{u})

if [ "$Local" = "$remote" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S %z')] [$$] [git]: Already up to date"
elif [ "$Local" = "$base" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S %z')] [$$] [git]: Changes detected! Pulling"
    git pull
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S %z')] [$$] [git]: Local and remote have diverged"
fi

# STEP 4: Start the app with Gunicorn
gunicorn -b 0.0.0.0:8000 "app:create_app()"
