import requests

from integrations.logging_config import *

logger = setup_logger(__name__)


class WebRequest():

    def __init__(self,url,method="get",data = None):
        try:
            logger.debug(f"webrequest init: {method}, {url}")
            if method == "get":
                response = requests.get(url, verify=False)
            elif method == "post":
                if data is None:
                    logger.info(f"webrequest init: data empty, but post, return")

                    self.status_code = -1
                    return
                response = requests.post(url, verify=False, data=data)
            else:
                logger.info(f"webrequest init: {method} invalid, return")
                self.status_code = -1
                return

            response.raise_for_status()

            self.response_text = response.content.decode()
            self.status_code = response.status_code

        except Exception as error:
            logger.info(f"webrequest init: error {error}, return")

            self.error_text = error
            self.status_code = -1
            return

    def get_response_code(self):
        logger.debug(f"webrequest response_code: {self.status_code}")
        return self.status_code

    def get_response_text(self):
        logger.info(f"webrequesst: response_text: {self.response_text}")
        return self.response_text
