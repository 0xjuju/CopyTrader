# Crypto Investment / Trading Software

1. Each day, This program searches through coingecko for tokens that appreciated in price by a substantial amount overnight, or in the
last 7 days. The transactions occurring days before the price-surge are analyzed, and any Swap transactions and their
wallet addresses are extracted. Bots are filtered out and wallets are saved to database. Webhooks are setup to receive
incoming tokens from wallets with the highest number of token bought pre-surge. Those token are given a score based on:

   - Number of top wallets holding
   - Number of all wallets holding
   - Number of social media references it has
   - Sentiment analysis for project narrative
   - Mentions on hit sites like Binance blogs etc.

2. A trading bot that scans pools like Uniswap for highly volatile token pools. Using volatility, volume and other
correlating factors to conduct trades.

## Table of Contents

- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)


## Usage

This program is not designed to be an open-source product, so the step to initialize this program will be extensive.

Let's start by setting up our environment variables:


**This program uses alchemy as the RPC provider. get your api keys from [here](https://www.alchemy.com/)**

```commandline
ALCHEMY_API_KEY: str
ALCHEMY_WEBHOOK_KEY: str
```

### You will need to add your local host for testing. Django default is 127.0.0.1
- LOCAL_HOST: str

# website for production, can be empty for local development
- ALLOWED_HOST_WEBSITE: str

# Webhooks tested using Ngrok https://ngrok.com/
NGROK_TEMP_HOST: str

# Determine which host to run the server. Ngrok is needed when testing webhooks locally
USE_NGROK: bool
RUN_MAIN: bool

# API Keys for commercial block explorers (bypasses the need for a full-nodes so we can get the closest block to a
given timestamp)
arbiscan.io
- ARBITRUM_API_KEY: str
bscscan.com
- BSC_API_KEY: str
etherscan.io
- ETHERSCAN_API_KEY: str
polygonscan.com
- POLYGONSCAN_API_KEY: str

# Database configuration. This project uses PostgresSQL for production, and the default Django SQL Lite for test
- DATABASE_URL: str
- DB_HOST: str
- DB_NAME: str
- DB_PASSWORD: str
- DB_PORT: int
- DB_USER: str

# Any wallet address for testing purposes
MY_WALLET_ADDRESS: str

REDIS_URL: str
# Django secret key located in settings
SECRET_KEY: str

# Used for automated text updates, but not used at the moment
TWILIO_ACCOUNT_SID: str = ""
TWILIO_AUTH_TOKEN: str = ""
TWILIO_NUMBER: str = ""

Setup project by doing the following steps:

1. In the terminal, run `python manage.py createsuperuser` to setup user and password for admin privileges.
2. Run `python manage.py` to run your server, and then navigate to your admin panel. Django default is http://127.0.0.1:8000/
3. Navigate to http://127.0.0.1:8000/admin/blockchain/chain/ and add the following case-sensitive chains the program will use:
 - ethereum
 - arbitrum-one
 - polygon-pos
 - binance-smart-chain
4. Factory contracts from DEXs are used to parse through each pool in the exchange. We need to set the factory contract
and abi manually. For now we'll use Uniswap V3 on ethereum. Navigate to http://127.0.0.1:8000/admin/blockchain/factorycontract/
to create FactoryContract model. Input the contract address '0x1F98431c8aD98523631AE4a59f267346ea31F984', and then head to
https://etherscan.io/address/0x1F98431c8aD98523631AE4a59f267346ea31F984#code to copy the contract JSON for the abi field
5. Next, we will need contract addresses for each token pool we're analyzing. We only need basic functions that exist
in most pool contracts, so let's grab a v2 and v3 contract and address from the following:
 - v3 v2 https://etherscan.io/address/0x4c54ff7f1c424ff5487a32aad0b48b19cbaf087f
 - https://etherscan.io/address/0xdfc14d2af169b0d36c4eff567ada9b2e0cae044f
 Navigate to http://127.0.0.1:8000/admin/blockchain/abi/ and create two new ABI models. Name them 'v3pools' and 'v2pools'
 respectively.
6. Now let's create filter for parsing through coingecko tokens. We need to set the number of pages to parse, and the
percent-of-increase for a token. Head to http://127.0.0.1:8000/admin/coingecko/geckofilter/ a create one model. Name it 'top_movers'
7. Run `python manage.py test` to ensure proper setup
8. Now let's run each command individually. In the terminal, run the following:
 - `python manage.py look_for_top_movers` which searches through each page of coingecko tokens, looking for tokens that
 increased by x percent. First run through may take some time to complete. Results are saved to databse.
  - `python manage.py update_wallets` enter user-input for the threshold of token-price-increases to search e.g. 80 to
  filter database for all token that increased by 80% in the last 24 hours or 7 days. All wallets that purchased the
  token before it surged will be saved to the database.
  - `python manage.py create_webhooks_for_wallet` This command will run function that ranks each wallet, and then pulls
  top n wallets, where n is the value set for the WalletFilter model. Head to http://127.0.0.1:8000/admin/wallets/walletfilter/
  to create one.
 9. Run your local NGROK server, and then navigate to https://www.alchemy.com/webhooks, click dashboard, and then send
 an ADDRESS_ACTIVITY webhook test to your NGROK server. This method simulates a token being bought by a top-wallet, and is
 handles by your webhook view located in blockchain.views. The transaction is parsed and the token is saved to the database

## To be Continued
- Scoring tokens based on different metrics such as social media, narratives, and online sentiment is under development.

- Each of the django commands we wrote in the terminal for each step of the program, will be written as celery tasks and
happen quietly in the background automatically. For now you can use a third-party scheduler on a server to run each
command periodically. For example Heroku Scheduler if you use Heroku as a deployment method.

- Once top-wallets are identified, further logic using gas-fee averages to further filter out bot will created

- NGROK for Django needs to be implemented so that we can use env variables RUN_MAIN and USE_NGROK to automatically
create Ngrok server for testing.

- Trading bot will be ran by a simple celery background tasks upon server start. It will continuously look for pools to
trade, making trades until volatility and volume break a certain threshold. Most paramters will be chose by a SVM machine
learning algorith, still under development.


## License

This project is licensed under the [License Name] License - see the [LICENSE](LICENSE) file for details.
