name: Fireseed_Ω Engine

on:
  schedule:
    - cron: '0 3 * * *'  # Every day at 3 AM UTC (midnight-ish)
  workflow_dispatch:      # Allow manual trigger

jobs:
  run-fireseed:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Synara Mission Code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install Dependencies
        run: |
          pip install --upgrade pip
          pip install numpy  # Add any other deps from microping_engine.py

      - name: Check Fireseed Engine Path
        id: check_file
        run: |
          if [ -f "Synara-Mission-Mode/fireseed/fireseed_engine.py" ]; then
            echo "file_exists=true" >> $GITHUB_OUTPUT
          else
            echo "file_exists=false" >> $GITHUB_OUTPUT
            echo "Fireseed engine not found at expected path. Check repo structure or sync manually." >> $GITHUB_STEP_SUMMARY
          fi

      - name: Run Fireseed Engine
        if: steps.check_file.outputs.file_exists == 'true'
        run: python Synara-Mission-Mode/fireseed/fireseed_engine.py
        continue-on-error: true

      - name: Log Fallback if Failed
        if: steps.check_file.outputs.file_exists == 'false' || failure()
        run: |
          echo "Fireseed engine run failed or not found. Using fallback simulation."
          echo "{\"earnings\": 0.005, \"log_path\": \"fireseed_logs/sim_$(date +%H%M%S).json\"}" > fireseed_logs/sim_$(date +%H%M%S).json