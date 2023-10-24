#!/bin/bash

# Path to app
SCRIPT_PATH="/path/to/app.py" # Path is not to be displayed on GitHub

# Function to check if the app is running
check_app() {
  # Check if the app is running by checking the process list
  if pgrep -f "$SCRIPT_PATH" > /dev/null; then
    return 0  # App is running
  else
    return 1  # App is not running
  fi
}

# Function to stop the app
stop_app() {
  if check_app; then
    pkill -f "$SCRIPT_PATH"
    echo "App stopped."
  fi
}

# Function to start the app
start_app() {
  nohup python3 "$SCRIPT_PATH" > /dev/null 2>&1 &
  echo "App started."
}

# Stop the app if it's running
stop_app

# Start the app
start_app