import requests

class WebRequest():

    def __init__(self,url,method="get",data = None):
        try:
            if method == "get":
                response = requests.get(url, verify=False)
            elif method == "post":
                if data is None:
                    self.status_code = -1
                    return
                response = requests.post(url, verify=False, data=data)
            else:
                self.status_code = -1
                return

            response.raise_for_status()

            self.response_text = response.content.decode()
            self.status_code = response.status_code

        except Exception as error:
            print (error)
            self.error_text = error
            self.status_code = -1
            return

    def get_response_code(self):
        return self.status_code

    def get_response_text(self):
        return self.response_text
