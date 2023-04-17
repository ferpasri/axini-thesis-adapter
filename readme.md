### Setup
Create a [virtual environment](https://docs.python.org/3/library/venv.html), activate it, and then run:

```bash
pip install -r requirements.txt
```

### Run
To start the Python adapter; go to the folder python_adapter in your terminal and run *"sudo python3 plugin_adapter.py --channel \<channel> --name \<name> --url \<websocket> --log_level \<loglevel> --token \<token>"* where:

- <name> is the of your machine, e.g. dev-vm
- <channel> is the channel.
- <loglevel> is the level of the logger shown in the terminal, either 1 (error), 2 (warning), 4 (into) or 8 (debugging).
- <token> is the token generated on the Adapter page within the AMP GUI.
- <websocket>  Additionally the websocket address for the adapter (ws(s)://..) can be found on the same page.

### Example

python3 plugin_adapter.py --channel extern --name Yannick --url "wss://research01.axini.com:443/adapters" --log_level 4 --token eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2ODk0OTk5OTMsInN1YiI6Inlhbm5pY2sudmFuLmRlci52bGV1dGVuQHN0dWRlbnQudXZhLm5sIiwiaXNzIjoidm1wdWJsaWNwcm9kMDEiLCJzY29wZSI6ImFkYXB0ZXIifQ.Tsrr0qtvVK5shwFzxMgQsndNg_oSXLE22ZV6nOA0adA