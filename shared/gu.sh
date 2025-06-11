#!/bin/bash
cd Web_Scracper_text/sub_portfolio/
git fetch origin
Local=$(git rev-parse @) 
remote=$(git rev-parse @{u}) 
base=$(git merge-base @ @{u}) 
if [ "$Local" = "$remote" ]; then echo "[$(date '+%Y-%m-%d %H:%M:%S %z')] [$$] [git]: Already upto date"
elif [ "$Local" = "$base" ]; then echo "[$(date '+%Y-%m-%d %H:%M:%S %z')] [$$] [git]: Changes detected! Pulling" 
git pull 
else echo "[$(date '+%Y-%m-%d %H:%M:%S %z')] [$$] [git]: Local and remote"
fi


cd ..
git fetch origin
Local=$(git rev-parse @) 
remote=$(git rev-parse @{u}) 
base=$(git merge-base @ @{u}) 
if [ "$Local" = "$remote" ]; then echo "[$(date '+%Y-%m-%d %H:%M:%S %z')] [$$] [git]: Already upto date"
elif [ "$Local" = "$base" ]; then echo "[$(date '+%Y-%m-%d %H:%M:%S %z')] [$$] [git]: Changes detected! Pulling" 
git pull 
else echo "[$(date '+%Y-%m-%d %H:%M:%S %z')] [$$] [git]: Local and remote"
fi

gunicorn -b 0.0.0.0:8000 "app: create_app()"