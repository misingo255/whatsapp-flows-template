from fastapi import APIRouter, UploadFile, File, status
from fastapi.responses import JSONResponse
from utilities.middleware import WhatsappFlowsMiddleware
from database.models import FlowData
from database.schemas import FlowDataSchema


flows_router = APIRouter()


@flows_router.post("/create")
async def create_flow(flow_name: str):
    flow = FlowData.get_all()
    if flow:
        return JSONResponse(
            content="FLOW ALREADY EXISTS",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    created_flow_id = WhatsappFlowsMiddleware.create_flow(flow_name)
    if not created_flow_id:
        return JSONResponse(
            content="FLOW CREATION FAILED",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    _flow_data = FlowDataSchema(flow_name=flow_name, flow_id=created_flow_id)
    flow_data = _flow_data.dict(exclude_unset=True)
    flow_data = FlowData(**flow_data)
    flow_data.save()
    return JSONResponse(content=created_flow_id, status_code=status.HTTP_201_CREATED)


@flows_router.post("/upload")
async def upload_flow_json(flow_id: str, file: UploadFile = File(...)):
    flow = FlowData.by_id(flow_id)
    if not flow:
        return JSONResponse(
            content="FLOW NOT FOUND, PLEASE CREATE A FLOW FIRST",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    if flow.is_uploaded:
        return JSONResponse(
            content="FLOW ALREADY UPLOADED", status_code=status.HTTP_400_BAD_REQUEST
        )
    response = WhatsappFlowsMiddleware.upload_flow_json(flow_id, file)
    if not response:
        return JSONResponse(
            content="FLOW UPLOAD FAILED, VERIFY YOUR FLOW ID OR FILE",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    flow.is_uploaded = True
    flow.save()

    return JSONResponse(
        content=response,
        status_code=status.HTTP_200_OK,
    )


@flows_router.post("/publish")
async def publish_flow(flow_id: str):
    flow = FlowData.by_id(flow_id)
    if not flow:
        return JSONResponse(
            content="FLOW NOT FOUND, PLEASE CREATE A FLOW FIRST",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    if not flow.is_uploaded:
        return JSONResponse(
            content="FLOW NOT UPLOADED, PLEASE UPLOAD FIRST",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    if flow.is_published:
        return JSONResponse(
            content="FLOW NOT UPLOADED, PLEASE UPLOAD FIRST",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    response = WhatsappFlowsMiddleware.publish_flow(flow_id)
    if not response:
        return JSONResponse(
            content="FLOW PUBLISH FAILED",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    flow.is_published = True
    flow.save()

    return JSONResponse(content=response, status_code=status.HTTP_200_OK)


@flows_router.post("/send")
async def send_flow(flow_id: str, recipient_phone_number: str):
    flow = FlowData.by_id(flow_id)
    if not flow:
        return JSONResponse(
            content="FLOW NOT FOUND, PLEASE CREATE A FLOW FIRST",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    if not flow.is_uploaded:
        return JSONResponse(
            content="FLOW NOT UPLOADED, PLEASE UPLOAD FIRST",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    if flow.is_published:
        response = WhatsappFlowsMiddleware.send_published_flow(
            flow_id, recipient_phone_number
        )
        if not response:
            return JSONResponse(
                content="FLOW SENDING FAILED", status_code=status.HTTP_400_BAD_REQUEST
            )
        return JSONResponse(content=response, status_code=status.HTTP_200_OK)
    else:
        response = WhatsappFlowsMiddleware.send_unpublished_flow(
            flow_id, recipient_phone_number
        )
        if not response:
            return JSONResponse(
                content="FLOW SENDING FAILED", status_code=status.HTTP_400_BAD_REQUEST
            )
        return JSONResponse(content=response, status_code=status.HTTP_200_OK)
