# Crypto Investment / Trading Software

## Description
This program searches through coingecko for tokens that recently appreciated in price by a substantial amount.
Transactions occurring days before the price-surge are analyzed, and any Swap events and associated wallets are extracted.
Bots are filtered out, and wallets are saved to a database. Webhooks are initiated to listen for incoming tokens for
wallets with the highest number of tokens bought pre-surge. Tokens are ranked based on:

   - Number of top wallets holding the token.
   - Number of all wallets holding the token.
   - Number of social media references it has.
   - Sentiment analysis for project narrative.
   - Mentions on blogs like Binance etc.

## Table of Contents

- [Usage](#usage)
- [License](#license)


## Usage
Let's start by setting up our environment variables:


This program uses alchemy as the RPC provider. get your api keys from [here](https://www.alchemy.com/)

```commandline
ALCHEMY_API_KEY: str
ALCHEMY_WEBHOOK_KEY: str
```

You will need to add your local host for testing. Django default is 127.0.0.1
```commandline
LOCAL_HOST: str
```

Website for production. It can be empty for local development
```commandline
ALLOWED_HOST_WEBSITE: str
```

Webhooks tested using [Ngrok](https://ngrok.com/)
```commandline
NGROK_TEMP_HOST: str
```

Determine which host to run the server. Ngrok is needed when testing webhooks locally
```commandline
USE_NGROK: bool
RUN_MAIN: bool
```

API Keys for commercial block explorers (bypasses the need for a full-nodes so we can get the closest block to a
given timestamp)

arbiscan.io
```commandline
ARBITRUM_API_KEY: str
```
bscscan.com
```commandline
BSC_API_KEY: str
```
etherscan.io
```commandline
ETHERSCAN_API_KEY: str
```
polygonscan.com
```commandline
POLYGONSCAN_API_KEY: str
```

Database configuration. This project uses PostgresSQL for production, and the default Django SQL Lite for test 
```commandline
DATABASE_URL: str
DB_HOST: str
DB_NAME: str
DB_PASSWORD: str
DB_PORT: int
DB_USER: str
```

Any wallet address. For testing purposes
```commandline
MY_WALLET_ADDRESS: str
```

Message broker for backend tasks
```commandline
REDIS_URL: str
```
Django secret key located in settings
```commandline
SECRET_KEY: str
```

Used for automated text updates, but not used at the moment
```commandline
TWILIO_ACCOUNT_SID: str = ""
TWILIO_AUTH_TOKEN: str = ""
TWILIO_NUMBER: str = ""
```

The webhook endpoint where wallet activity will be sent and handled
```commandline
WEBHOOK_WALLET_ACTIVITY_ENDPOINT: str
```

### Run project be following the steps below:

1. In the terminal, run `python manage.py createsuperuser` to set up username and password for admin privileges.
2. Run `python manage.py` to run your server, and then navigate to your admin panel. Django default is http://127.0.0.1:8000/
3. Navigate to http://127.0.0.1:8000/admin/blockchain/chain/ and add the following case-sensitive chains the program will use:
   - ethereum
   - arbitrum-one
   - polygon-pos
 4. Factory contracts from DEXs are used to parse through each pool in the exchange. We need to set the factory contract
 and abi manually. For now, we'll use Uniswap V3 on ethereum. Navigate to http://127.0.0.1:8000/admin/blockchain/factorycontract/
 to create FactoryContract model. Input the contract address '0x1F98431c8aD98523631AE4a59f267346ea31F984', and then head to
 [this ether scan address](https://etherscan.io/address/0x1F98431c8aD98523631AE4a59f267346ea31F984#code) to copy the contract's 
 JSON for the abi field.
5. Next, we will need contract addresses for each token pool that we're analyzing. We only need basic functions that exist
in most pool contracts, so let's grab a v2 and v3 contract and address from etherscan:
   - [v3 pool](https://etherscan.io/address/0x4c54ff7f1c424ff5487a32aad0b48b19cbaf087f)
   - [v2 pool](https://etherscan.io/address/0xdfc14d2af169b0d36c4eff567ada9b2e0cae044f)
   
6. Navigate to http://127.0.0.1:8000/admin/blockchain/abi/ and create two new ABI models. Name them 'v3pools' and 'v2pools'
 respectively. Create one more named `balance_of` and set the text to `[{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"}]`

7. Now let's create a filter for parsing through coingecko tokens. We need to set the number of pages to parse, and the
percent-of-increase attribute for a token. Head to http://127.0.0.1:8000/admin/coingecko/geckofilter/. Create one model.
Name it 'top_movers'
8. Run `python manage.py test wallets.tests.test_update_wallets.TestUpdateWallets.test_updater` to ensure proper setup.
Each step of how the wallet updater works will be explained in the console.
9. Now let's run each command individually. In the terminal, run the following:
   - `python manage.py look_for_top_movers` Search through each page of coingecko tokens, looking for tokens that
   increased by x percent. The first run through may take some time to complete.
   - `python manage.py update_wallets` Enter user-input for the threshold of token-price-increases to search e.g. 80 to
   filter database for all token that increased by 80% in the last 24 hours or 7 days. All wallets that purchased the
   token before it surged will be saved to the database.
   - `python manage.py filter_wallets_for_bots` Filter through all wallets marked as non-human and either mark them
   as bots and remove them, or mark them as human.
   - `python manage.py create_webhooks_for_wallet` Create webhooks for list of wallets for each chain in blockchain.chains
   model. Head to http://127.0.0.1:8000/admin/wallets/walletfilter/ to create filters for ranked wallets.
10. Run your local NGROK server using `ngrok http http://localhost:8000`, then add the https value to `NGROK_TEMP_HOST`
   in your environment variables.
11. Navigate to the [Alchemy Webhooks](https://www.alchemy.com/webhooks) page, click dashboard, navigate to the 'ADDRESS_ACTIVITY' webhook, and then 
send a test to your NGROK server. This method simulates a token being bought by a top-wallet, and is handled by your 
webhook view located in `blockchain.views`. The transaction is parsed and the token data is saved to the database.

12. Each iteration of `update_wallets` and `filter_wallets_for_bots` in conjunction with waller filter options will yield
a different group of wallets. You will need to run `python manage.py replace_webhook_wallets` to replace the list of 
webhook addresses on each chain.

## To be Continued
- Scoring tokens based on different metrics such as social media, narratives, and online sentiment is under development.

- Each of the django commands we wrote in the terminal for each step of the program, will be written as celery tasks that
happen quietly in the background. For now, you can use a third-party scheduler on a server to run each
command periodically e.g. Heroku Scheduler if you use Heroku as a deployment method.

- NGROK for Django needs to be implemented so that we can use env variables `RUN_MAIN=False` and `USE_NGROK=True` to 
automatically create Ngrok server for testing.

- Trading bot will be run by a simple celery background task upon server start. It will continuously look for pools to
trade, making trades until volatility and volume break a certain threshold. Most parameters will be chosen by an SVM 
machine learning algorith.


## License

This project is licensed under the [License Name] License - see the [GNU Affero General Public License](LICENSE) file for details.
