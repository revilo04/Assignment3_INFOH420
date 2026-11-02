#!/bin/zsh
# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Configure local Airflow directory inside the project
export AIRFLOW_HOME="$(pwd)/airflow_home"
export AIRFLOW__CORE__LOAD_EXAMPLES=False
export NO_PROXY="*"  # Prevents macOS fork() crashes with requests/urllib3 in Airflow

mkdir -p "$AIRFLOW_HOME"
if [ ! -L "$AIRFLOW_HOME/dags" ]; then
    ln -s "$(pwd)/dags" "$AIRFLOW_HOME/dags"
fi

echo "Starting Airflow Standalone at http://localhost:8080 ..."
airflow standalone