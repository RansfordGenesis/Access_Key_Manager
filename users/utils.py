from decouple import config
from trycourier import Courier


client = Courier(auth_token=config('COURIER_TOKEN'))


def send_mail_verification(email:str, link:str):
    client.send_message(
  message={
    "to": {
      "email": email,
    },
    "template": "W9B4WK8FZG43FWQDS7YZHB07YYM0",
    "data": {
      "link": link,
    },
  }
)
    
def send_reset_mail(email:str, link:str):
    client.send_message(
        message={
            "to": {
                "email": email,
            },
            "template": "SNS3G5YBS24CEWQYCA5N72Q3GBKM",
            "data": {
                "link": link,
            },
        }
    )
