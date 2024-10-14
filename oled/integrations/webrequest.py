import requests

from integrations.logging_config import *
import config.online as cfg_online


logger = setup_logger(__name__)


class WebRequest():
    response_text = ""
    response_code = -1

    def __init__(self,url,method="get",data = None):
        try:
            client_cert_key = cfg_online.ONLINE_CLIENT_KEY
            client_cert_crt = cfg_online.ONLINE_CLIENT_CERT

            if not os.path.isfile(client_cert_key): raise Exception("KEYFILE_NOT_EXISTS")
            if not os.path.isfile(client_cert_crt): raise Exception("CRTFILE_NOT_EXISTS")
            client_cert = (client_cert_crt,client_cert_key)
            logger.debug (f"client_cert: {client_cert}")
        except Exception as error:
            client_cert = None
            logger.debug(f"client cert error: {error}")

        try:
            logger.debug(f"webrequest init: {method}, {url}, {client_cert}")
            if method == "get":
                response = requests.get(url, verify=False, cert=client_cert)
            elif method == "post":
                if data is None:
                    logger.debug(f"webrequest init: data empty, but post, return")

                    self.response_code = -1
                    return
                response = requests.post(url, verify=False, data=data, cert=client_cert)
            else:
                logger.debug(f"webrequest init: {method} invalid, return")
                response_text = ""
                self.response_code = -1
                return

            response.raise_for_status()

            self.response_text = response.content.decode()
            self.response_code = response.status_code

        except Exception as error:
            logger.info(f"webrequest init: error {error}, return")

            self.error_text = error
            self.response_code = -1
            return

    def get_response_code(self):
        logger.debug(f"webrequest response_code: {self.response_code}")
        return self.response_code

    def get_response_text(self):
        logger.debug(f"webrequesst: response_text: {self.response_text}")
        return self.response_text
