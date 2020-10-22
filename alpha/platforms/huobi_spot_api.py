# -*- coding:utf-8 -*-

"""
Huobi Spot Api Module.

Author: Daisy
Date:   2020/09/10
Email:  ***
"""

import gzip
import json
import copy
import hmac
import base64
import urllib
import hashlib
import datetime
import time
from urllib.parse import urljoin
from alpha.utils.request import AsyncHttpRequests
from alpha.const import USER_AGENT


__all__ = ("HuobiSpotRestAPI", )

class HuobiSpotRestAPI:
    """ Huobi Spot REST API Client.

    Attributes:
        host: HTTP request host.
        access_key: Account's ACCESS KEY.
        secret_key: Account's SECRET KEY.
        passphrase: API KEY Passphrase.
    """

    def __init__(self, host, access_key, secret_key):
        """ initialize REST API client. """
        self._host = host
        self._access_key = access_key
        self._secret_key = secret_key


    async def get_etp_reference(self, etpName=None):
        """ Get ETP Reference
        
        Args:
            spot_code:  such as "BTCUSDT".
        
        Returns:
            success: Success results, otherwise it's None.
            error: Error information, otherwise it's None.
        
        * NOTE: 1. If input `spot_code`, only matching this spot code.
                2. If not input 'spot_code', matching all spot_codes.
        """
        uri = "/v2/etp/reference"
        params = {}
        if etp_code:
            params["etpName"] = etpName
        success, error = await self.request("GET", uri, params)
        return success, error


    async def get_orderbook(self, symbol, depth=None):
        """ Get orderbook information.

        Args:
            contract_code:  such as "BTCUSDT".

        Returns:
            success: Success results, otherwise it's None.
            error: Error information, otherwise it's None.
        """
        uri = "/market/depth"
        params = {
            "symbol": symbol,
            "type": "step0"
        }

        if depth:
            params["depth"] = depth
        success, error = await self.request("GET", uri, params=params)
        return success, error
    
    async def get_klines(self, symbol, period, size=None):
        """ Get kline information.

        Args:
            contract_code:  such as "BTCUSDT".
            period: 1min, 5min, 15min, 30min, 60min,4hour,1day, 1mon
            size: [1,2000]

        Returns:
            success: Success results, otherwise it's None.
            error: Error information, otherwise it's None.
        """
        uri = "/market/history/kline"
        params = {
            "symbol": symbol,
            "period": period,
        }
        if size:
            params["size"] = size
        
        success, error = await self.request("GET", uri, params=params)
        return success, error
    

    async def get_etp_nav(self, symbol):
        """ Get ETP NAV.

        Args:
            etp_code: such as "BTCUSDT"
        
        Returns:
            success: Success results.
            error: Error information.
        """
        uri = "/market/etp"
        params = {
            "symbol": symbol
        }
        success, error = await self.request("GET", uri, params=params)
        return success, error

    
    async def create_order(self, account_id, symbol, _type, amount, price=None, source="spot-api", client_order_id=None, stop_price=None, operater=None):
        """ Create an new order.

        Args:
            account_id: "spot"/"margin"/"super margin".
            symbol: such as "btcl3".
            type: order type, such as "buy-market"/"sell market"/"buy-limit".
            amount: order amount
            price: Order price.
            source: "spot-api"/"margin-api"/"super-margin-api"/"c2c-margin-api"
           
        Returns:
            success: Success results, otherwise it's None.
            error: Error information, otherwise it's None.
        """
        uri = "/v1/order/orders/place"
        body = {
            "account-id": account_id,
            "symbol": symbol,
            "type": _type,
            "amount": amount
        }
        if client_order_id:
            body.update({"client_order_id": client_order_id})
        if price:
            body.update({"price": price})
        if source:
            body.update({"source": souce})
        if stop_price:
            body.update({"stop_price": stop_price})
        if operater:
            body.update({"operator": operator})
        success, error = await self.request("POST", uri, body=body, auth=True)
        return success, error
    
    async def create_orders(self, source="spot-api", orders_data):
        """ Batch Create orders.
            orders_data = {'orders_data': [
               {  
                'account-id':'spot',  'symbol':'btcl3', 
                'type':'buy-market', 'amount':'10', 'price':'10', 'source':'spot-api', 
                'client-order-id':'', 'stop-price':'', 'operator':'>='},
               { 
                'account-id':'spot',  'symbol':'btcl3', 
                'type':'buy-market', 'amount':'10', 'price':'10', 'source':'spot-api', 
                'client-order-id':'', 'stop-price':'', 'operator':'>='}]}   
        """
        uri = "/v1/order/batch-orders"
        body = orders_data
        success, error = await self.request("POST", uri, body=body, auth=True)
        return success, error
        

    async def revoke_order(self, order_id=""):
        """ Revoke an order.

        Args:
            contract_code: such as "BTC-USDT".
            order_id: Order ID.

        Returns:
            success: Success results, otherwise it's None.
            error: Error information, otherwise it's None.
        """
        uri = "/v1/order/orders/"+order_id+"/submitcancel"
        body = {
            "order_id": order_id
        }
        success, error = await self.request("POST", uri, body=body, auth=True)
        return success, error


    async def revoke_client_order(self, client_order_id=""):
        """ Revoke an order.

        Args:
            contract_code: such as "BTC-USDT".
            order_id: Order ID.

        Returns:
            success: Success results, otherwise it's None.
            error: Error information, otherwise it's None.
        """
        uri = "/v1/order/orders/submitCancelClientOrder"
        body = {
            "client-order-id": client_order_id
        }
        success, error = await self.request("POST", uri, body=body, auth=True)
        return success, error

    async def revoke_orders(self, order_ids=[], client_order_ids=[]):
        """ Revoke multiple orders.

        Args:
            client_order_ids: Client Order ID list.
            order_ids: Order ID list.

        Returns:
            success: Success results, otherwise it's None.
            error: Error information, otherwise it's None.
        """
        uri = "/v1/order/orders/batchcancel"
        body = {
            "order_id": ",".join(order_ids),
            "client_order_id": ",".join(client_order_ids)
        }
        success, error = await self.request("POST", uri, body=body, auth=True)
        return success, error

    async def revoke_open_orders(self, account_id="", symbol=[], side="", size=None):
        """ Revoke all orders.

        Args:
            account_id: 'spot'/'margin'/'super-margin'
            symbol: symbol list.
            side: 'buy' or 'sell'
            size: [0, 100]

        Returns:
            success: Success results, otherwise it's None.
            error: Error information, otherwise it's None.

        * NOTE: 1. If input `contract_code`, only matching this contract code.
                2. If not input `contract_code`, matching by `symbol + contract_type`.
        """
        uri = "/v1/order/orders/batchCancelOpenOrders"
        body = { }
        if account_id:
            body.update({"account_id": account_id})
        if symbol:
            body.update({"symbol": ",".join(symbol)})
        if side:
            body.update({"side": side})
        if size:
            body.update({"size": size})

        success, error = await self.request("POST", uri, body=body, auth=True)
        return success, error

    async def get_order_info(self, contract_code, order_ids=[], client_order_ids=[]):
        """ Get order information.

        Args:
            contract_code: such as "BTC-USDT".
            order_ids: Order ID list. (different IDs are separated by ",", maximum 20 orders can be requested at one time.)
            client_order_ids: Client Order ID list. (different IDs are separated by ",", maximum 20 orders can be requested at one time.)

        Returns:
            success: Success results, otherwise it's None.
            error: Error information, otherwise it's None.
        """
        uri = "/linear-swap-api/v1/swap_order_info"
        body = {
            "contract_code": contract_code,
            "order_id": ",".join(order_ids),
            "client_order_id": ",".join(client_order_ids)
        }
        success, error = await self.request("POST", uri, body=body, auth=True)
        return success, error
    
    async def get_order_detail(self, order_id):
        """ Get Order Detail

        Args:
            order_id: order id.
       
        """
        uri = "/v1/order/orders/"+order_id
        body = {
            "order_id": order_id
        }
        success, error = await self.request("POST", uri, body=body, auth=True)
        return success, error

    async def get_open_orders(self, account_id, symbol, side="", _from="", direct="", size=100):
        """ Get open order information.

        Args:
            account_id: account id-'spot'/'margin'/'super-margin'
            symbol: such as 'btcl3usdt'
            side: 'buy' or 'sell'
            from: starting id
            direct: 'prev' or 'next'
            size: num of orders

        Returns:
            success: Success results, otherwise it's None.
            error: Error information, otherwise it's None.
        """
        uri = "/v1/order/openOrders"
        body = {
            "account-id": account_id,
            "symbol": symbol,
            "size": size
        }
        if side:
            body.update({"side": side})
        if _from:
            body.update({"from": _from})
        if direct:
            body.update({"direct": direct})

        success, error = await self.request("POST", uri, body=body, auth=True)
        return success, error


    async def create_etp(self, etpName, value, curency):
        """ ETP Creation

        Args:
            etpName: etp name
            value: value of creation
            currency: as 'USDT'

        """
        uri = "/v2/etp/creation"
        body = {
            "etpName": etpName,
            "value": value,
            "currency": currency
        }
        success, error = await self.request("POST", uri, body=body, auth=True)
        return success, error

    async def redempt_etp(self, etpName, currency, amount):
        """ ETP Redemption

        Args:
            etpName: etp name
            currency: as 'USDT'
            amount: redemption amount
        """
        uri = "/v2/etp/redemption"
        body = {
            "etpName": etpName,
            "currency": currency,
            "amount": amount
        }
        success, error = await self.request("POST", uri, body=body, auth=True)
        return success, error

     async def get_orderbook(self, symbol, depth=None):
        """ Get orderbook information.

        Args:
            contract_code:  such as "BTCUSDT".

        Returns:
            success: Success results, otherwise it's None.
            error: Error information, otherwise it's None.
        """
        uri = "/market/depth"
        params = {
            "symbol": symbol,
            "type": "step0"
        }

        if depth:
            params["depth"] = depth
        success, error = await self.request("GET", uri, params=params)
        return success, error

    async def get_etp_transactions(self, etpNames=[], currencies=[], transactTypes="", transactStatus="", startTime=None, endTime=None, sort="", limit=100, fromId=None):
        """ Get ETP Transaction Record

        Args:
            etpNames: ETP list.
            currencies: denominated currency.
            transactTypes: 'creation'/'redemption'/missing-"all"
            transactStatus: 'completed'/'processing'/'clearing'/'rejected'/missing-'all'
            sort: 'asc'/'desc'
            limit: largest items returned on one page
            fromId: starting order id

        Returns:
            success: Success results, otherwise it's None.
            error: Error information, otherwise it's None.
        """
        uri = "/v2/etp/transactions"
        params={
            "limit": limit
        }
        if etpNames:
            params["etpNames"] = ",".join(etpNames)
        if currencies:
            params["currencies"] = ",".join(currencies)
        if transactTypes:
            params["transactTypes"] = ",".join(transactTypes)
        if transactStatus:
            params["transactStatus"] = ",".join(transactStatus)
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if sort:
            params["sort"] = sort
        if fromID:
            params["fromID"] = fromID
        success, error = await self.request("GET", uri, params=params)
        return success, error  

    async def get_etp_transaction(self, transactId):
        """ Get Specific ETP Transaction Record

        Args:
            transactId: transaction ID

        Returns:
            success: Success results, otherwise it's None.
            error: Error information, otherwise it's None.
        """
        uri = "/v2/etp/transaction"
        params = {
            "transactId": transactId
        }
        success, error = await self.request("GET", uri, params=params)
        return success, error  

    async def get_etp_rebalance(self, symbol, rebalTypes=[], startTime=None, endTime=None, sort="", limit=100, fromId=None):
        """ Get ETP Rebalance Record

        Args:
            symbol: ETP Name.
            rebalTypes: rebalance type
            sort: 'asc'/'desc'
            limit: largest items returned on one page
            fromId: starting order id

        Returns:
            success: Success results, otherwise it's None.
            error: Error information, otherwise it's None.
        """
        uri = "/v2/etp/rebalance"
        params = {
            "symbol": symbol
            "limit": limit
        }
        if rebalTypes:
            params["rebalTypes"] = ",".join(rebalTypes)
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if sort:
            params["sort"] = sort
        if fromId:
            params["fromId"] =fromId

        success, error = await self.request("GET", uri, params=params)
        return success, error  

    # TODO:

    async def get_history_orders(self, symbol, types=[], start_time=None, end_time=None, start_date="", end_date="", states=[], _from="", direct="", size=""):
        """ Get history orders information.

        Args:
            symbol: such as "btcl3usdt".
            types: 'buy-market', 'sell-market', 'buy-limit', 'sell-limit', 'buy-ioc', 'sell-ioc', 'buy-limit-maker', 'sell-limit-maker', 'buy-stop-limit'，'sell-stop-limit', 'buy-limit-fok', 'sell-limit-fok', 'buy-stop-limit-fok', 'sell-stop-limit-fok'
            start_time: UTC time in millisecond
            end_time: UTC time in millisecond
            start_date: "yyyy-mm-dd"
            end_date: "yyyy-mm-dd"
            states: 'submitted', 'partial-filled', 'partial-canceled', 'filled', 'canceled'，'created'
            from: starting ID
            direct: query direction, 'prev'/'next'
            size: size of query record

        
        Returns:
            success: Success results, otherwise it's None.
            error: Error information, otherwise it's None.

        """
        uri = "/v1/order/orders"
        params = {
            "symbol": symbol,
            "states": states
        }
        if types:
            params["states"] = ",".join(states)
        if start_time:
            params["start-time"] = start_time
        if end_time:
            params["end-time"] = end_time
        if start_date:
            params["start-date"] = start_date
        if end_date:
            params["end-date"] = end_date
        if _from:
            params["from"] = _from
        if direct:
            params["direct"] = direct
        if size:
            params["size"] = size

        success, error = await self.request("GET", uri, params=params)
        return success, error    

    async def transfer_between_spot_future(self, symbol, amount, type_s):
        """ Do transfer between spot and future.
        Args:
            symbol: currency,such as btc,eth,etc.
            amount: transfer amount.pls note the precision digit is 8.
            type_s: "pro-to-futures","futures-to-pro"

        """
        body = {
                "currency": symbol,
                "amount": amount,
                "type": type_s
                }

        uri = 'https://api.huobi.pro/v1/futures/transfer'

        success, error = await self.request("POST", uri, body=body, auth=True)
        return success, error
    
    async def request(self, method, uri, params=None, body=None, headers=None, auth=False):
        """ Do HTTP request.

        Args:
            method: HTTP request method. `GET` / `POST` / `DELETE` / `PUT`.
            uri: HTTP request uri.
            params: HTTP query params.
            body: HTTP request body.
            headers: HTTP request headers.
            auth: If this request requires authentication.

        Returns:
            success: Success results, otherwise it's None.
            error: Error information, otherwise it's None.
        """
        if uri.startswith("http://") or uri.startswith("https://"):
            url = uri
        else:
            url = urljoin(self._host, uri)

        if auth:
            timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
            params = params if params else {}
            params.update({"AccessKeyId": self._access_key,
                           "SignatureMethod": "HmacSHA256",
                           "SignatureVersion": "2",
                           "Timestamp": timestamp})

            params["Signature"] = self.generate_signature(method, params, uri)

        if not headers:
            headers = {}
        if method == "GET":
            headers["Content-type"] = "application/x-www-form-urlencoded"
            headers["User-Agent"] = USER_AGENT
            _, success, error = await AsyncHttpRequests.fetch("GET", url, params=params, headers=headers, timeout=10)
        else:
            headers["Accept"] = "application/json"
            headers["Content-type"] = "application/json"
            headers["User-Agent"] = USER_AGENT
            _, success, error = await AsyncHttpRequests.fetch("POST", url, params=params, data=body, headers=headers,
                                                              timeout=10)
        if error:
            return None, error
        if not isinstance(success, dict):
            result = json.loads(success)
        else:
            result = success
        if result.get("status") != "ok":
            return None, result
        return result, None

    def generate_signature(self, method, params, request_path):
        if request_path.startswith("http://") or request_path.startswith("https://"):
            host_url = urllib.parse.urlparse(request_path).hostname.lower()
            request_path = '/' + '/'.join(request_path.split('/')[3:])
        else:
            host_url = urllib.parse.urlparse(self._host).hostname.lower()
        sorted_params = sorted(params.items(), key=lambda d: d[0], reverse=False)
        encode_params = urllib.parse.urlencode(sorted_params)
        payload = [method, host_url, request_path, encode_params]
        payload = "\n".join(payload)
        payload = payload.encode(encoding="UTF8")
        secret_key = self._secret_key.encode(encoding="utf8")
        digest = hmac.new(secret_key, payload, digestmod=hashlib.sha256).digest()
        signature = base64.b64encode(digest)
        signature = signature.decode()
        return signature
