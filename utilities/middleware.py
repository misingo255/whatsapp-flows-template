import uuid
import json
from dotenv import load_dotenv
import os
import requests

load_dotenv()


WHATSAPP_BUSINESS_PHONE_NUMBER_ID = os.getenv("WHATSAPP_BUSINESS_PHONE_NUMBER_ID", "")
WHATSAPP_BUSINESS_ACCESS_TOKEN = os.getenv("WHATSAPP_BUSINESS_ACCESS_TOKEN", "")
WHATSAPP_BUSINESS_ACCOUNT_ID = os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID", "")


class WhatsappFlowsMiddleware:
    auth_header = {"Authorization": f"Bearer {WHATSAPP_BUSINESS_ACCESS_TOKEN}"}
    messaging_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {WHATSAPP_BUSINESS_ACCESS_TOKEN}",
    }
    base_url = "https://graph.facebook.com/v20.0"

    @classmethod
    def create_flow(cls, flow_name: str):
        flow_base_url = f"{cls.base_url}/{WHATSAPP_BUSINESS_ACCOUNT_ID}/flows"
        flow_creation_payload = {"name": flow_name, "categories": '["OTHER"]'}
        flow_create_response = requests.post(
            flow_base_url, headers=cls.auth_header, json=flow_creation_payload
        )
        created_flow_id = flow_create_response.json().get("id")
        return created_flow_id

    @classmethod
    def upload_flow_json(cls, flow_id: str, file: str):
        graph_assets_url = f"{cls.base_url}/{flow_id}/assets"
        flow_asset_payload = {"name": file, "asset_type": "FLOW_JSON"}
        files = {"file": (file, open(file, "rb"), "application/json")}
        response = requests.post(
            graph_assets_url,
            headers=cls.auth_header,
            data=flow_asset_payload,
            files=files,
        )
        return response

    @classmethod
    def publish_flow(cls, flow_id: str):
        flow_publish_url = f"{cls.base_url}/{flow_id}/publish"
        response = requests.post(flow_publish_url, headers=cls.auth_header)
        return response

    @classmethod
    def send_published_flow(cls, flow_id: str, recipient_phone_number: str):
        flow_token = str(uuid.uuid4())
        flow_payload = {
            "type": "flow",
            "header": {"type": "text", "text": "MSAIDIZI WA KUKATA TIKETI YA BOTI"},
            "body": {
                "text": "Habari, Karibu ZAN FAST FERRIES. Tafadhali jaza fomu hii ili kupata tiketi ya boti.",
            },
            "footer": {
                "text": "Bonyeza, KATA TIKETI YA BOTI ili kuendea hatua inayofuata"
            },
            "action": {
                "name": "flow",
                "parameters": {
                    "flow_message_version": "3",
                    "flow_token": flow_token,
                    "flow_id": flow_id,
                    "flow_cta": "KATA TIKETI YA BOTI",
                    "flow_action": "navigate",
                    "flow_action_payload": {"screen": "BINAFSI"},
                },
            },
        }

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": str(recipient_phone_number),
            "type": "interactive",
            "interactive": flow_payload,
        }

        messaging_url = f"{cls.base_url}/{WHATSAPP_BUSINESS_PHONE_NUMBER_ID}/messages"
        response = requests.post(
            messaging_url, headers=cls.messaging_headers, json=payload
        )
        return response

    @classmethod
    def send_unpublished_flow(cls, flow_id: str, recipient_phone_number: str):
        flow_token = str(uuid.uuid4())
        flow_payload = {
            "type": "flow",
            "header": {"type": "text", "text": "MSAIDIZI WA KUKATA TIKETI YA BOTI"},
            "body": {
                "text": "Habari, Karibu ZAN FAST FERRIES. Tafadhali jaza fomu hii ili kupata tiketi ya boti.",
            },
            "footer": {
                "text": "Bonyeza, KATA TIKETI YA BOTI ili kuendea hatua inayofuata"
            },
            "action": {
                "name": "flow",
                "parameters": {
                    "flow_message_version": "3",
                    "flow_token": flow_token,
                    "flow_id": flow_id,
                    "flow_cta": "KATA TIKETI YA BOTI",
                    "flow_action": "navigate",
                    "mode": "draft",
                    "flow_action_payload": {"screen": "BINAFSI"},
                },
            },
        }

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": str(recipient_phone_number),
            "type": "interactive",
            "interactive": flow_payload,
        }

        messaging_url = f"{cls.base_url}/{WHATSAPP_BUSINESS_PHONE_NUMBER_ID}/messages"
        response = requests.post(
            messaging_url, headers=cls.messaging_headers, json=payload
        )
        return response

    @classmethod
    def send_message(cls, message: str, phone_number: str):
        payload = {
            "messaging_product": "whatsapp",
            "to": str(phone_number),
            "type": "text",
            "text": {"preview_url": False, "body": message},
        }
        messaging_url = f"{cls.base_url}/{WHATSAPP_BUSINESS_PHONE_NUMBER_ID}/messages"
        response = requests.post(
            messaging_url, headers=cls.messaging_headers, json=payload
        )
        return response

    @classmethod
    def flow_reply_processor(cls, data):
        # Extract the relevant JSON response from the data structure
        flow_response = ["entry"][0]["changes"][0]["value"]["messages"][0][
            "interactive"
        ]["nfm_reply"]["response_json"]
        flow_data = json.loads(flow_response)

        # Extract values from flow_data
        jina_la_kwanza = flow_data.get("jina_la_kwanza")
        jina_la_kati = flow_data.get("jina_la_kati")
        jina_la_mwisho = flow_data.get("jina_la_mwisho")
        jinsia_id = flow_data.get("jinsia")
        namba_ya_simu = flow_data.get("namba_ya_simu")
        uraia_id = flow_data.get("uraia")
        nchi = flow_data.get("nchi")
        mkoa = flow_data.get("mkoa")
        kutoka_id = flow_data.get("kutoka")
        kwenda_id = flow_data.get("kwenda")
        tarehe_ya_safari = flow_data.get("tarehe_ya_safari")
        idadi_ya_wasafiri = flow_data.get("idadi_ya_wasafiri")
        boti_la_kusafiria_id = flow_data.get("boti_la_kusafiria")

        match jinsia_id:
            case "ME":
                jinsia = "Mwanaume (ME)"
            case "KE":
                jinsia = "Mwanamke (KE)"

        match uraia_id:
            case "mtanzania":
                uraia = "Mtanzania"
            case "mgeni":
                uraia = "Mgeni"

        match kutoka_id:
            case "DAR":
                kutoka = "Dar es salaam (DAR)"
            case "MKO":
                kutoka = "Mkoani (MKO)"
            case "TAN":
                kutoka = "Tanga (TAN)"
            case "WET":
                kutoka = "Wete (WET)"
            case "ZNZ":
                kutoka = "Zanzibar (ZNZ)"

        match kwenda_id:
            case "DAR":
                kwenda = "Dar es salaam (DAR)"
            case "MKO":
                kwenda = "Mkoani (MKO)"
            case "TAN":
                kwenda = "Tanga (TAN)"
            case "WET":
                kwenda = "Wete (WET)"
            case "ZNZ":
                kwenda = "Zanzibar (ZNZ)"

        match boti_la_kusafiria_id:
            case "sea_star_01":
                boti_la_kusafiria = "Sea Star 01"
            case "zanzibar_01":
                boti_la_kusafiria = "Zanzibar 01"
            case "zanzibar_02":
                boti_la_kusafiria = "Zanzibar 02"

        # Format the response message
        reply = (
            f"Asante kwa kujaza fomu! Haya ni maelezo tuliyopokea:\n\n"
            f"*Jina la Kwanza:* {jina_la_kwanza}\n"
            f"*Jina la Kati:* {jina_la_kati}\n"
            f"*Jina la Mwisho:* {jina_la_mwisho}\n"
            f"*Jinsia:* {jinsia}\n"
            f"*Namba ya Simu:* {namba_ya_simu}\n"
            f"*Uraia:* {uraia}\n"
            f"*Nchi:* {nchi}\n"
            f"*Mkoa:* {mkoa}\n"
            f"*Kutoka:* {kutoka}\n"
            f"*Kwenda:* {kwenda}\n"
            f"*Tarehe ya Safari:* {tarehe_ya_safari}\n"
            f"*Idadi ya Wasafiri:* {idadi_ya_wasafiri}\n"
            f"*Boti la Kusafiria:* {boti_la_kusafiria}"
        )

        # Extract the user's phone number to send the reply
        user_phone_number = ["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
        response = cls.send_message(reply, user_phone_number)
        return response
