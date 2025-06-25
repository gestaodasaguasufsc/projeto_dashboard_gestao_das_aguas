name: py

on:
  schedule:
    - cron: "00 00 * * *"    #runs at 00:00 UTC everyday

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      
      - name: execute py script # run file
        run: |
          python schedule.py