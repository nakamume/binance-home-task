## Binance Home Exercise
It's a take home exercise for binance interview process.

## Problem Statement
### Assignment
- Use public market data from the SPOT API at https://api.binance.com
- Binance API spot documentation is at https://github.com/binance-exchange/binance-official-api-docs/
- All answers should be provided as source code written in either Go, Python, Java, Rust, and/or Bash.

### Questions:
1. Print the top 5 symbols with quote asset BTC and the highest volume over the last 24 hours in descending order.
2. Print the top 5 symbols with quote asset USDT and the highest number of trades over the last 24 hours in descending order.
3. Using the symbols from Q1, what is the total notional value of the top 200 bids and asks currently on each order book?
4. What is the price spread for each of the symbols from Q2?
5. Every 10 seconds print the result of Q4 and the absolute delta from the previous value for each symbol.
6. Make the output of Q5 accessible by querying http://localhost:8080/metricsusing the Prometheus Metrics format.

Upload all to github and share a link

## How to run
### The Docker way
I have pushed `nakamume/binance-home-task` docker image.

```bash
docker run -p 8080:8080 -e API_KEY="<YOUR_BINANCE_API_KEY>" -e API_SECRET="<YOUR_BINANCE_API_SECRET>" nakamume/binance-home-task --data=q1
```

### Going Old-School
[poetry](https://python-poetry.org/) is used for dependency management. Following cmds assume that you have poetry installed and configured.<br/>
Get Binance API Key and Secret API Key. You can get keys for testnet from [here](https://testnet.binance.vision/)

```bash
git clone git@github.com:nakamume/binance-home-task.git # clone this repo
poetry install
poetry run python binance/main.py --help

# to run for Question 1
export API_KEY=<YOUR_BINANCE_API_KEY>
export API_SECRET=<YOUR_BINANCE_API_SECRET>
poetry run python binance/main.py --data=q1
```