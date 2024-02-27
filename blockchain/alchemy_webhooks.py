
import json
import requests
from typing import Any

import decouple


class Webhook:
    def __init__(self):
        self.WEBHOOK_URL = "https://dashboard.alchemy.com/api/"
        self.WEBHOOK_KEY = decouple.config("ALCHEMY_WEBHOOK_KEY")

        self.networks = {
            "ethereum": "ETH_MAINNET",
            "arbitrum-one": "ARB_MAINNET",
            "polygon-pos": "MATIC_MAINNET",
            "ETH_MAINNET": "ethereum",
            "ARB_MAINNET": "arbitrum-one",
            "MATIC_MAINNET": "polygon-pos",
        }

        self.WEBHOOK_OPTIONS = [
            "ADDRESS_ACTIVITY",
            "MINED_TRANSACTION",
            "GRAPHQL",
            "DROPPED_TRANSACTION",
            "NFT_ACTIVITY",
            "NFT_METADATA_UPDATE"
        ]

    def _make_request(self, endpoint: str, chain: str, webhook_type: str, payload_opts: dict) -> dict[str, Any]:
        """

        :param endpoint: API endpoint
        :param chain: blockchain network
        :param webhook_type: type of webhook for subscription
        :param payload_opts: query parameters
        :return: json response from Alchemy webhooks server
        """

        network = self.networks[chain]

        url = self.WEBHOOK_URL + endpoint
        if webhook_type not in self.WEBHOOK_OPTIONS:
            raise ValueError(f"{webhook_type} not a valid option from {self.WEBHOOK_OPTIONS}")

        payload = {
            "network": network,
            "webhook_type": webhook_type,
            "webhook_url": None
        }
        if payload_opts:
            payload.update(payload_opts)

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "X-Alchemy-Token": self.WEBHOOK_KEY,
        }

        response = requests.post(url, json=payload, headers=headers)

        return response.json()

    def create_swap_events_for_wallet_webhook(self, chain: str, webhook_url: str, address_list: list[str]) -> dict:
        query = """{{
          block {{
            logs(filter: {{addresses: ["0x6D76F7d16CA40dD13E52dF3E1615318f763c0241"], topics: [[], [], ["0xC05189824bF36f2ad9d0f64a222c1C156Df28DA1"] ]}}) {{
              transaction {{
                hash
                index
                from {{
                  address
                }}
                to {{
                  address
                }}
                logs {{
                  topics
                }}
                type
                status
              }}
            }}
          }}
        }}""".format(topics=json.dumps(
            [[], [], ["0xC05189824bF36f2ad9d0f64a222c1C156Df28DA1"]]
        ))
        print(query)
        payload = {
            "webhook_url": webhook_url,
            "graphql_query": query
        }

        return self._make_request("create-webhook", chain=chain, webhook_type="GRAPHQL", payload_opts=payload)

    def create_wallet_activity_webhook(self, chain: str, webhook_url: str, webhook_type: str, address_list: list[str]) -> dict[str, Any]:
        """
        Subscribe list of wallets for webhook
        :param chain: blockchain network
        :param webhook_url: endpoint to send webhook data
        :param webhook_type: webhook type for subscriptions
        :param address_list: list of addresses to subscribe to
        :return: None
        """

        payload = {
            "addresses": address_list,
            "webhook_url": webhook_url
                   }

        r = self._make_request("create-webhook", chain=chain, webhook_type=webhook_type, payload_opts=payload)
        return r

    def delete_webhook(self, webhook_id: str) -> dict:
        headers = {
            "accept": "application/json",
            "X-Alchemy-Token": f"{self.WEBHOOK_KEY}"
        }
        url = f"https://dashboard.alchemy.com/api/delete-webhook?webhook_id={webhook_id}"

        return requests.delete(url, headers=headers).json()

    def get_address_list_from_webhook(self, webhook_id: str, limit=100, page_cursor=0) -> dict[str, Any]:
        """

        :param webhook_id: webhook id
        :param limit: max values per page
        :param page_cursor: start page
        :return:
        """
        url = f"https://dashboard.alchemy.com/api/webhook-addresses?webhook_id={webhook_id}&limit={limit}&after={page_cursor}"

        headers = {
            "accept": "application/json",
            "X-Alchemy-Token": self.WEBHOOK_KEY,
        }

        response = requests.get(url, headers=headers)
        return response.json()

    def get_all_webhooks(self) -> list[dict[str, Any]]:
        """
        All subscribed webhooks
        :return: List of subscribed webhooks
        """
        url = self.WEBHOOK_URL + "team-webhooks"
        headers = {
            "accept": "application/json",
            "X-Alchemy-Token": self.WEBHOOK_KEY
        }
        response = requests.get(url, headers=headers)

        return response.json()

    def replace_webhook_address_list(self, webhook_id: str, address_list: list[str]):
        """
        replace entire list of addresses with new ones
        :param webhook_id: ID of webhook subscription
        :param address_list: New list of addresses to replace old
        :return:
        """
        url = "https://dashboard.alchemy.com/api/update-webhook-addresses"
        payload = {
            "webhook_id": webhook_id,
            "addresses": address_list,
        }

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "X-Alchemy-Token": self.WEBHOOK_KEY,
        }

        response = requests.put(url, json=payload, headers=headers)
        print(response)


