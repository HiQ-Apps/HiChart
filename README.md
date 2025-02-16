<img width="500" alt="Hi" src="https://github.com/user-attachments/assets/0e2ec058-e1c4-4a73-b9b7-e568bdac5828" />

### HiChart
![Hit and Run](https://github.com/user-attachments/assets/8aa46de7-dd1f-4bf5-aa07-e3a878ac8953)
HiChart was born in Pinescript version 6 over on TradingView. Great app and website, but it lacks a lot of automation tools especially when it comes to multiple tickers.
So I set out to import everything into Python. A few weeks later, HiChart was born. HiChart uses one of my technical indicators, John Carter's TTM Squeeze. It scans
200 of the top tickers daily(tickers.txt), appends it to historical data inside a sleek SQLite setup. Then fires signals via websocket to a Discord channel.
#
![Hit and Run (2)](https://github.com/user-attachments/assets/ba769248-56d3-4953-a406-16b72668dc2c)
```sh
git clone https://github.com

cd hi-chart

pip install -r requirements.txt
```
#
```sh
# Run the project
python main.py
```
#
![Hit and Run (3)](https://github.com/user-attachments/assets/c7db7c40-accc-4eac-abf7-e335e0e9a48a)

Feel Free to submit issues and pull requests
#
![Hit and Run (4)](https://github.com/user-attachments/assets/691e90aa-5308-4e63-ac3e-f3799c01f31e)

This project is licensed under [MIT License](LICENSE)
