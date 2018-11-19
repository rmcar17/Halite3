@echo off
set /p times="Times to run: " 
set /p size="Enter Map Size (1-5): "
set /a size="size*8+24"
set /p id="Enter Bot Number: "

for /l %%x in (1, 1, %times%) do (
  halite.exe --replay-directory replays/ -vvv --width %size% --height %size% "python MyBot.py" "python oldBots/MyBot%id%.py"
)
pause