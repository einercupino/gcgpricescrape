"""
gundam_prices.py
=================

This module exposes a `search_prices` function that accepts a Gundam
trading card code (for example, ``GD04-041``) and returns a list of
price records from several retailers.  Results include 401 Games,
Banana Games, Hobbiesville, and TCGplayer (via TCGCSV), with prices
converted to CAD using the latest Bank of Canada exchange rate when
available.  Each record contains the abbreviated store name, product
title, price in CAD, and available quantity (when provided by the
store's API).

The implementation uses asynchronous/concurrent techniques to fetch
product data efficiently while being courteous to the underlying
Shopify endpoints.  A fallback mechanism for TCGplayer searches
ensures that cards are found even if their set prefix is not mapped
exactly in the group map.
"""

import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

# Default HTTP headers for JSON requests.  Reuse these across all
# functions to reduce duplication and ensure a consistent user agent
# string.  Accepting JSON helps Shopify and TCGCSV endpoints return
# structured data instead of HTML redirects when possible.
HEADERS_JSON: dict[str, str] = {
    "User-Agent": "GundamPriceAPI/1.0",
    "Accept": "application/json",
}

# Abbreviations for store names used in output.  These help shorten
# the display lines in comparison tables and align with user requests.
STORE_ABBREV = {
    "401 Games": "401G",
    "Banana Games": "BANG",
    "Hobbiesville": "HOBB",
    "TCGplayer": "TCGP",
}

# Maps Gundam set abbreviations to their corresponding TCGCSV group IDs.
# If new sets are released you can add their abbreviations and groupIds
# here.  Promos and token sets are included as well.  A generic
# mapping for resource tokens (prefix "R") is also provided.
GROUP_MAP = {
    # Main Sets
    "GD01": 24221,
    "GD02": 24408,
    "GD03": 24522,
    "GD04": 24633,
    "GD05": 24699,

    # Starter Decks
    "ST01": 24222,
    "ST02": 24223,
    "ST03": 24224,
    "ST04": 24225,
    "ST05": 24407,
    "ST06": 24409,
    "ST07": 24410,
    "ST08": 24411,
    "ST09": 24625,
    "ST10": 24692,

    # Extra Boosters
    "EB01": 24693,

    # Promos / Tokens
    "RP": 24372,
    "EXRP": 24373,
    "EXBP": 24374,
    "GCG-PR": 24340,

    # Alias for resource tokens
    "R": 24372,
}

def normalize_tags(raw_tags) -> List[str]:
    """Normalize Shopify tags whether returned as a comma-separated string or list.

    Args:
        raw_tags: The raw tags value from the Shopify product.  This may be
            a comma-separated string or a list.

    Returns:
        A list of uppercase tag strings with surrounding whitespace removed.
    """
    if isinstance(raw_tags, str):
        return [t.strip().upper() for t in raw_tags.split(",") if t.strip()]
    elif isinstance(raw_tags, list):
        return [str(t).strip().upper() for t in raw_tags if str(t).strip()]
    return []


def get_usd_cad_rate() -> Optional[float]:
    """Fetch the current USD to CAD exchange rate from the Bank of Canada.

    This function uses the Valet API RSS feed from the Bank of Canada
    (FXUSDCAD series) to obtain the daily spot rate.  It parses the XML
    and extracts the first <cb:value> element, which represents the
    exchange rate expressed as CAD per USD.  If the request or parsing
    fails, ``None`` is returned.

    Returns:
        The USD to CAD exchange rate as a float, or ``None`` on failure.
    """
    url = "https://www.bankofcanada.ca/valet/fx_rss/FXUSDCAD"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/xml",
    }
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code != 200:
            return None
        root = ET.fromstring(resp.content)
        namespaces = {'cb': 'http://www.bankofcanada.ca/valet/'}
        for val in root.iterfind('.//cb:value', namespaces):
            text = val.text
            if text:
                try:
                    return float(text)
                except ValueError:
                    continue
        return None
    except Exception:
        return None


def _request_json(url: str, headers: dict[str, str], timeout: int = 20) -> Optional[dict]:
    """Helper to fetch JSON data with basic error handling.

    Returns a parsed JSON object on success or None on error.
    """
    try:
        resp = requests.get(url, headers=headers, timeout=timeout)
        if resp.status_code != 200:
            return None
        return resp.json()
    except Exception:
        return None


def _find_product_handles_401(code: str, headers: dict[str, str]) -> List[str]:
    """Search 401 Games Gundam singles collection for products containing the code."""
    base_url = "https://store.401games.ca"
    collection = "gundam-card-game-singles"
    page = 1
    code_upper = code.upper()
    matches: List[str] = []
    while True:
        url = (
            f"{base_url}/collections/{collection}/products.json"
            f"?limit=250&page={page}"
        )
        data = _request_json(url, headers)
        if not data:
            break
        products = data.get("products", [])
        if not products:
            break
        for product in products:
            title = product.get("title", "").upper()
            if code_upper in title:
                handle = product.get("handle")
                if handle:
                    matches.append(handle)
        page += 1
        # Short sleep to reduce load
        import time
        time.sleep(0.25)
    return matches


def _find_product_handles_banana(code: str, headers: dict[str, str]) -> List[str]:
    """Search Banana Games Gundam singles collection for products containing the code."""
    base_url = "https://bananagames.ca"
    collection = "gundam-singles"
    page = 1
    code_upper = code.upper()
    tag_key = f"NUMBER_{code_upper}"
    matches: List[str] = []
    while True:
        url = (
            f"{base_url}/collections/{collection}/products.json"
            f"?limit=250&page={page}"
        )
        data = _request_json(url, headers)
        if not data:
            break
        products = data.get("products", [])
        if not products:
            break
        for product in products:
            title = product.get("title", "").upper()
            tags = normalize_tags(product.get("tags", ""))
            if code_upper in title or tag_key in tags:
                handle = product.get("handle")
                if handle:
                    matches.append(handle)
        page += 1
        import time
        time.sleep(0.25)
    return matches


def _find_product_handles_hobbiesville(code: str, headers: dict[str, str]) -> List[str]:
    """Search Hobbiesville's Gundam singles collection for products containing the code."""
    base_url = "https://hobbiesville.com"
    collection = "gundam-card-game-singles"
    page = 1
    code_upper = code.upper()
    tag_key = f"NUMBER_{code_upper}"
    matches: List[str] = []
    while True:
        url = (
            f"{base_url}/collections/{collection}/products.json"
            f"?limit=250&page={page}"
        )
        data = _request_json(url, headers)
        if not data:
            break
        products = data.get("products", [])
        if not products:
            break
        for product in products:
            title = product.get("title", "").upper()
            tags = normalize_tags(product.get("tags", ""))
            if code_upper in title or tag_key in tags:
                handle = product.get("handle")
                if handle:
                    matches.append(handle)
        page += 1
        import time
        time.sleep(0.25)
    return matches


def fetch_401_products(card_code: str) -> List[Dict[str, Optional[str]]]:
    """Retrieve Near Mint variants for a card from 401 Games."""
    headers = HEADERS_JSON
    handles = _find_product_handles_401(card_code, headers)
    results: List[Dict[str, Optional[str]]] = []

    def _fetch_handle(handle: str) -> List[Dict[str, Optional[str]]]:
        detail_url = f"https://store.401games.ca/products/{handle}.json"
        data = _request_json(detail_url, headers)
        if not data:
            return []
        product = data.get("product", {})
        title = product.get("title", "")
        out: List[Dict[str, Optional[str]]] = []
        for variant in product.get("variants", []):
            condition = variant.get("title", "") or ""
            if condition.strip().upper() != "NM":
                continue
            price_str = variant.get("price")
            try:
                price = float(price_str)
            except (TypeError, ValueError):
                continue
            quantity = variant.get("inventory_quantity")
            out.append({
                "store": STORE_ABBREV["401 Games"],
                "title": title,
                "price": price,
                "quantity": quantity,
            })
        return out

    if not handles:
        return results
    with ThreadPoolExecutor(max_workers=min(5, len(handles))) as pool:
        futures = {pool.submit(_fetch_handle, h): h for h in handles}
        for fut in as_completed(futures):
            try:
                res = fut.result()
                if res:
                    results.extend(res)
            except Exception:
                continue
    return results


def fetch_banana_products(card_code: str) -> List[Dict[str, Optional[str]]]:
    """Retrieve Near Mint variants for a card from Banana Games."""
    headers = HEADERS_JSON
    handles = _find_product_handles_banana(card_code, headers)
    results: List[Dict[str, Optional[str]]] = []

    def _fetch_handle(handle: str) -> List[Dict[str, Optional[str]]]:
        detail_url = f"https://bananagames.ca/products/{handle}.json"
        data = _request_json(detail_url, headers)
        if not data:
            return []
        product = data.get("product", {})
        title = product.get("title", "")
        tags = normalize_tags(product.get("tags", ""))
        rarity = None
        printing = None
        for tag in tags:
            tag_upper = tag.upper()
            if tag_upper.startswith("RARITY_"):
                rarity = tag.split("_", 1)[-1]
            if tag_upper.startswith("PRINTING_"):
                printing = tag.split("_", 1)[-1]
        out: List[Dict[str, Optional[str]]] = []
        for variant in product.get("variants", []):
            condition = variant.get("title", "") or ""
            if condition.strip().lower() != "near mint":
                continue
            price_str = variant.get("price")
            try:
                price = float(price_str)
            except (TypeError, ValueError):
                continue
            out.append({
                "store": STORE_ABBREV["Banana Games"],
                "title": title,
                "price": price,
                "quantity": None,
            })
        return out

    if not handles:
        return results
    with ThreadPoolExecutor(max_workers=min(5, len(handles))) as pool:
        futures = {pool.submit(_fetch_handle, h): h for h in handles}
        for fut in as_completed(futures):
            try:
                res = fut.result()
                if res:
                    results.extend(res)
            except Exception:
                continue
    return results


def fetch_hobbiesville_products(card_code: str) -> List[Dict[str, Optional[str]]]:
    """Retrieve Near Mint variants for a card from Hobbiesville."""
    headers = HEADERS_JSON
    handles = _find_product_handles_hobbiesville(card_code, headers)
    results: List[Dict[str, Optional[str]]] = []

    def _fetch_handle(handle: str) -> List[Dict[str, Optional[str]]]:
        detail_url = f"https://hobbiesville.com/products/{handle}.json"
        data = _request_json(detail_url, headers)
        if not data:
            return []
        product = data.get("product", {})
        title = product.get("title", "")
        tags = normalize_tags(product.get("tags", ""))
        rarity = None
        printing = None
        for tag in tags:
            tag_upper = tag.upper()
            if tag_upper.startswith("RARITY_"):
                rarity = tag.split("_", 1)[-1]
            if tag_upper.startswith("PRINTING_"):
                printing = tag.split("_", 1)[-1]
        out: List[Dict[str, Optional[str]]] = []
        for variant in product.get("variants", []):
            condition = variant.get("title", "") or ""
            if condition.strip().lower() != "near mint":
                continue
            price_str = variant.get("price")
            try:
                price = float(price_str)
            except (TypeError, ValueError):
                continue
            out.append({
                "store": STORE_ABBREV["Hobbiesville"],
                "title": title,
                "price": price,
                "quantity": None,
            })
        return out

    if not handles:
        return results
    with ThreadPoolExecutor(max_workers=min(5, len(handles))) as pool:
        futures = {pool.submit(_fetch_handle, h): h for h in handles}
        for fut in as_completed(futures):
            try:
                res = fut.result()
                if res:
                    results.extend(res)
            except Exception:
                continue
    return results


def _find_tcg_product(card_code: str, headers: dict[str, str]) -> Optional[tuple[int, int, str]]:
    """Locate a TCGCSV product by card code and return its productId and groupId.

    The card code (e.g. ``GD04-041``) includes a set abbreviation before
    the hyphen.  We use this abbreviation to look up the corresponding
    groupId from ``GROUP_MAP``, then scan that group's products for a
    matching ``Number`` extendedData value.  If found, the productId,
    groupId and product name are returned.  If the product or group
    cannot be determined, ``None`` is returned.  A fallback search across
    all groups is attempted when a direct match is not found.
    """
    code_upper = card_code.upper().strip()
    # Determine group prefix with fallbacks.  Resource cards map to RP,
    # and suffixed prefixes (e.g. GD01_B) fall back to the base prefix
    # if necessary.
    if code_upper.startswith("R-"):
        prefix = "R"
    else:
        prefix = code_upper.split('-')[0]
    if prefix not in GROUP_MAP:
        base = prefix.split('_')[0]
        if base in GROUP_MAP:
            prefix = base
    group_id = GROUP_MAP.get(prefix)
    if not group_id:
        return None
    def search_group(gid: int) -> Optional[tuple[int, int, str]]:
        products_url = f"https://tcgcsv.com/tcgplayer/86/{gid}/products"
        try:
            resp = requests.get(products_url, headers=headers, timeout=30)
            if resp.status_code != 200:
                return None
            data = resp.json()
        except Exception:
            return None
        for result in data.get("results", []):
            extended = result.get("extendedData", [])
            for item in extended:
                name = item.get("name", "").strip().upper()
                value = item.get("value", "").strip().upper()
                if name == "NUMBER" and code_upper in value:
                    product_id = result.get("productId")
                    product_name = result.get("name")
                    return (product_id, gid, product_name)
        return None
    # First search within the mapped group
    match = search_group(group_id)
    if match:
        return match
    # Fallback: search across all groups when no direct match is found
    for gid in GROUP_MAP.values():
        if gid == group_id:
            continue
        match = search_group(gid)
        if match:
            return match
    return None


def fetch_tcg_products(card_code: str) -> List[Dict[str, Optional[str]]]:
    """Retrieve market price data for a card from TCGCSV and convert to CAD."""
    headers = {
        "User-Agent": "GundamPriceAPI/1.0",
        "Accept": "application/json",
    }
    match = _find_tcg_product(card_code, headers)
    if not match:
        return []
    product_id, group_id, product_name = match
    prices_url = f"https://tcgcsv.com/tcgplayer/86/{group_id}/prices"
    try:
        resp = requests.get(prices_url, headers=headers, timeout=30)
        if resp.status_code != 200:
            return []
        data = resp.json()
    except Exception:
        return []
    usd_to_cad = get_usd_cad_rate()
    results: List[Dict[str, Optional[str]]] = []

    # Iterate through all price objects for this group.  We join by
    # productId and ignore other products in the same group.  If the
    # exchange rate isn't available, prices remain in USD.  We round
    # converted prices to two decimals for consistency with CAD display.
    for price_obj in data.get("results", []):
        if price_obj.get("productId") != product_id:
            continue
        market_price = price_obj.get("marketPrice")
        if market_price is None:
            continue
        try:
            price_usd = float(market_price)
        except (TypeError, ValueError):
            continue
        # Convert USD to CAD if a rate is available
        price_cad = price_usd * usd_to_cad if usd_to_cad else price_usd
        # Round to two decimal places for currency
        price_cad = round(price_cad, 2)
        results.append({
            "store": STORE_ABBREV["TCGplayer"],
            "title": product_name,
            "price": price_cad,
            "quantity": None,
            "image": image_url
        })

    return results


def search_prices(card_code: str) -> List[Dict[str, Optional[str]]]:
    """Aggregate price results from all sources for the given card code.

    This is the main entry point for the API.  It concurrently
    fetches price data from 401 Games, Banana Games, Hobbiesville and
    TCGplayer, then concatenates all results into a single list.

    Args:
        card_code: The card code to search for (e.g. 'GD04-041').

    Returns:
        A list of price records; each is a dict with the abbreviated
        store name, product title, price in CAD, and quantity.
    """
    code = card_code.strip().upper()
    results: List[Dict[str, Optional[str]]] = []
    # Run store fetches concurrently to reduce total wait time
    with ThreadPoolExecutor(max_workers=4) as pool:
        future_401 = pool.submit(fetch_401_products, code)
        future_banana = pool.submit(fetch_banana_products, code)
        future_hob = pool.submit(fetch_hobbiesville_products, code)
        future_tcg = pool.submit(fetch_tcg_products, code)
        for fut in [future_401, future_banana, future_hob, future_tcg]:
            try:
                res = fut.result()
                if res:
                    results.extend(res)
            except Exception:
                continue
    return results