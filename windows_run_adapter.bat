@echo off
REM Create a Python virtual environment
python -m venv myenv

REM Activate the virtual environment
call myenv\Scripts\activate

REM Install dependencies from requirements.txt
pip install -r requirements.txt

REM Run the Python script with specified arguments
python plugin_adapter.py --channel controller --name autolink --url "wss://research01.axini.com:443/adapters" --log_level 4 --token addyourtokenhere
