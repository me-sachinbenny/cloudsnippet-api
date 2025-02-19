#!/bin/bash

# Define absolute paths to your backend and frontend directories
BACKEND_PATH="/Users/sachinbenny/Documents/Coder/Codebase/CloudSnippet/cloudsnippet-blog-api"
FRONTEND_PATH="/Users/sachinbenny/Documents/Coder/Codebase/CloudSnippet/cloudsnippet-blog"

# Start a new tmux session named 'dev_session' in detached mode
tmux new-session -d -s dev_session -n main

# Split the window vertically (top pane for the database)
tmux split-window -v -t dev_session:main

# Split the bottom pane horizontally (left for backend, right for frontend)
tmux split-window -h -t dev_session:main.1

# Select the top pane (0) and start the database
tmux send-keys -t dev_session:main.0 "cd $BACKEND_PATH && docker-compose -f mongodb_docker_compose.yml up -d" C-m

# Select the bottom-left pane (1) and start the backend
tmux send-keys -t dev_session:main.1 "cd $BACKEND_PATH && ./run.sh" C-m

# Select the bottom-right pane (2) and start the frontend
tmux send-keys -t dev_session:main.2 "cd $FRONTEND_PATH && npm run dev" C-m

# Attach to the tmux session
tmux attach-session -t dev_session