import datetime
import logging
import time
from typing import Dict, Iterable, Literal, Optional, TypedDict
import requests


# logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
_LOGGER = logging.getLogger(__name__)


class TmiAuthResponse(TypedDict):
    """Shape of the response to successful logins"""
    expiration: int
    refreshCountLeft: int
    refreshCountMax: int
    token: str


class TmiApiClient:
    """Client for the undocumented API on TMobile Home Internet gateways"""
    _BASE_URL: str = "http://192.168.12.1/TMI/v1/"
    _DEFAULT_HEADERS = {
        "accept": "application/json",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "max-age=0",
    }
    _auth_response: Optional[TmiAuthResponse] = None
    _auth_token: Optional[str] = None

    _username: str
    _password: str

    def __init__(
        self, username: str, password: str, loglevel: Optional[int] = None
    ) -> None:
        self._username = username
        self._password = password
        # if loglevel:
        #     logging.basicConfig(level=loglevel)


    def _get_auth_token(self) -> str:
        """Get a new auth token by logging in"""
        login_body = {"username": self._username, "password": self._password}

        login_response = requests.post(
            self._BASE_URL + "auth/login",
            json=login_body,
        )
        if not login_response.ok:
            login_response.raise_for_status()

        json_obj = login_response.json()

        response_auth_object: TmiAuthResponse = json_obj.get("auth", {})
        if not response_auth_object:
            raise RuntimeError(
                "failed to get token and expiration from request: %s",
                response_auth_object,
            )

        self._auth_token = response_auth_object["token"]
        self._auth_response = response_auth_object
        self._auth_expiration = datetime.datetime.utcfromtimestamp(
            self._auth_response.get("expiration", 0),
        )
        return self._auth_token

    def auth_token(self) -> str:
        """Get the authentication token by logging in"""
        if self._auth_token is None or self._auth_expiration is None:
            # logging.info("No previous token found, logging in")
            print("self._auth_token is None")
            return self._get_auth_token()

        if datetime.datetime.utcnow() > (
            self._auth_expiration - datetime.timedelta(seconds=10)
        ):
            # logging.info(
            #     "Token expired. Fetching new token."
            # )
            return self._get_auth_token()

        return self._auth_token

    def _get_headers(self) -> Dict[str, str]:
        """Get the headers for the request, including the auth token"""
        return {
            **self._DEFAULT_HEADERS,
            "Authorization": f"Bearer {self.auth_token()}",
        }

    def get(self, *args, **kwargs) -> Dict:
        """Thin wrapper around requests.get to handle authentication."""
        spec_headers = kwargs.pop("headers") if "headers" in kwargs else {}
        response = requests.get(
            *args, **kwargs, headers={**spec_headers, **self._get_headers()}
        )

        return response.json()

    def get_gateway_config(self) -> Dict:
        """Get the gateway's device, signal, and time"""
        return self.get(self._BASE_URL + "gateway?get=all")

    def get_gateway_signal(self) -> Dict:
        """Get the gateway's signal data."""
        return self.get(self._BASE_URL + "gateway?get=signal")

    def get_cell(self) -> Dict:
        """Get the gateway's cell data."""
        return self.get(self._BASE_URL + "network/telemetry/?get=cell")

    def get_sim(self) -> Dict:
        """Get the gateway's sim data."""
        return self.get(self._BASE_URL + "network/telemetry/?get=sim")

    def get_clients(self) -> Dict:
        """Get the gateway's clients."""
        return self.get(self._BASE_URL + "network/telemetry/?get=clients")

    def get_ap_config(self, retries: Optional[int] = 0, retry_seconds: Optional[int] = 1) -> Dict:
        """Get the access point config."""
        _retries = retries+1
        _error = 408

        # Gateway gets busy after an update and returns HTTP 408 until stable.
        while _error == 408 and _retries > 0:
            result = self.get(self._BASE_URL + "network/configuration/v2?get=ap")
            if "result" in result:
                # Error returned, not data
                _error = result['result']['statusCode']
                _retries -= 1
                _LOGGER.debug(f"Error {str(_error)} getting access_point data; {_retries} retries left")
                if _retries > 0:
                   time.sleep(retry_seconds)
            else:
                # Successful GET
                _error = 200
                _LOGGER.debug(f"Success getting access_point data")

        if _error != 200:
            raise Exception("Error {error} retrieving access_point data")
        return result

    def set_ap_config(self, new_ap_config: Dict):
        """Set the access point config."""
        try:
            result = requests.post(
                self._BASE_URL + "network/configuration/v2?set=ap",
                json=new_ap_config,
                headers={**self._get_headers()}
            )
            _LOGGER.debug(f"Success setting access_point data")
            return result
        except Exception as exc:
            _LOGGER.debug(f"Error {str(exc)} setting access_point data")
            raise

    def reboot_gateway(self):
        """Reboot the gateway."""
        return requests.post(
            self._BASE_URL + "gateway/reset?set=reboot",  
            headers={**self._get_headers()}
        )

    def disable_wifi(
        self,
        bands: Iterable[Literal["2.4ghz", "5.0ghz"]] = ["2.4ghz", "5.0ghz"],
    ):
        """Disable wifi on the specified bands. Both bands by default.
        This will cause the router to restart, so it's incredibly unlikely it
        will return successfully.

        Args:
            bands: List of bands to enable WiFi radio on
        """
        config = self.get_ap_config()
        for band in bands:
            config[band]["isRadioEnabled"] = False

        return self.set_ap_config(config)

    def enable_wifi(
        self,
        bands: Iterable[Literal["2.4ghz", "5.0ghz"]] = ["2.4ghz", "5.0ghz"],
    ):
        """Enable wifi on the specified bands. Both bands by default.
        This will cause the router to restart, so it's incredibly unlikely it
        will return successfully.

        Args:
            bands: List of bands to enable WiFi radio on
        """
        config = self.get_ap_config()
        for band in bands:
            config[band]["isRadioEnabled"] = True

        return self.set_ap_config(config)

    def get_version(self):
        """Get the API version string."""
        return self.get(self._BASE_URL + "version")


if __name__ == "__main__":
    cl = TmiApiClient("admin", "your.password.here")
    # print(cl.disable_wifi(['2.4ghz']))
    # print(cl.enable_wifi(['2.4ghz']))
    print(cl.get_ap_config())
    print(cl.get_version())
