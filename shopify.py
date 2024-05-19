import requests
import pprint
import json
from urllib.parse import urljoin
from typing import Dict, List
from requests import get


class Shopify:
    @staticmethod
    def format_url(url: str) -> str:
        """
        Remove URL query strings
        """

        url = url.split("?")[0]
        if not url.endswith("/"):
            url += "/"

        return url

    @staticmethod
    def retrieve_whole_json(url :str) -> dict:
        """
        Ger json from all pages
        """
        page = 1
        agg_data = []
    
        while True:
            page_url = url + f"/products.json?page={str(page)}"
            response = requests.get(page_url)
            data = response.json()
            page_has_products = "products" in data and len(
                data["products"]) > 0

            if not page_has_products:
                break
            agg_data.extend(data["products"])
            page += 1
        return agg_data

    @staticmethod
    def get_products(url: str) -> List[Dict[str, str]]:
        """
        Get collection's products
        """
        content = Shopify.retrieve_whole_json(url)
        content = {"products": content}
        

        return [
            {
                "id": product["id"],
                "title": product["title"],
                "url": urljoin(url, "/products/" + product["handle"]),
                "brand": product["vendor"],
                "images": [
                    {
                        "id": image["id"],
                        "src": image["src"], 
                        "height": image["height"],
                        "width": image["width"],
                        "position": image["position"],
                        "created_at": image["created_at"],        
                        "available": Shopify.get_available_status(
                            image.get("available", "N/A")
                        ),
                    }
                    for image in product.get("images", [])
                ]
            }
            for product in content["products"]
        ]

    @staticmethod
    def get_available_status(value) -> int:
        """
        Get available status
        """

        if value == True:
            return 1
        elif value == False:
            return 0
        else:
            return -1

    @staticmethod
    def get_shopify_config(url: str) -> Dict[str, str]:
        """
        Get the Shopify configuration
        """

        try:
            url = urljoin(url, "/cart.js")
            content = get(url).json()

            return content
        except:
            return None

    @staticmethod
    def is_collection(url: str) -> bool:
        """
        Check if the URL is a valid collection
        """
        if not "/collections/" in url:
            return False

        try:
            products = Shopify.get_products(url)

            return len(products) > 0
        except:
            return False

