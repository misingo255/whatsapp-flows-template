from fastapi import Request, status, BackgroundTasks, Response, APIRouter
from fastapi.responses import JSONResponse
from utilities.middleware import WhatsappFlowsMiddleware
from dotenv import load_dotenv
from database.models import FlowData
import os


load_dotenv()

WHATSAPP_BUSINESS_VERIFY_TOKEN = os.getenv("WHATSAPP_BUSINESS_VERIFY_TOKEN", "")


webhook_router = APIRouter()


@webhook_router.get("/webhook")
async def wehbook_verification(request: Request):
    if (
        request.query_params.get("hub.verify_token") == WHATSAPP_BUSINESS_VERIFY_TOKEN
        and request.query_params.get("hub.mode") == "subscribe"
    ):
        contents = request.query_params.get("hub.challenge")
        return Response(
            content=contents, media_type="text/plain", status_code=status.HTTP_200_OK
        )
    else:
        return JSONResponse(
            content="Invalid request", status_code=status.HTTP_400_BAD_REQUEST
        )


@webhook_router.post("/webhook")
async def webhook_processing(request: Request, tasks: BackgroundTasks):
    data = await request.json()
    messages = data["entry"][0]["changes"][0]["value"].get("messages")
    if messages:
        text = messages[0].get("text")
        user_phone_number = data["entry"][0]["changes"][0]["value"]["contacts"][0][
            "wa_id"
        ]

        if text:
            flow = FlowData.first_data()
            if flow.is_published:
                tasks.add_task(
                    WhatsappFlowsMiddleware.send_published_flow,
                    flow.flow_id,
                    user_phone_number,
                )
            else:
                tasks.add_task(
                    WhatsappFlowsMiddleware.send_unpublished_flow,
                    flow.flow_id,
                    user_phone_number,
                )
        else:
            tasks.add_task(WhatsappFlowsMiddleware.flow_reply_processor, data)
    return JSONResponse(
        content="CHAT MESSAGE PROCESSED SUCCESSFULL", status_code=status.HTTP_200_OK
    )
