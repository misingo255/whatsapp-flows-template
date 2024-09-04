from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.responses import JSONResponse
from utilities.middleware import WhatsappFlowsMiddleware
from database.models import FlowData
from database.schemas import FlowDataSchema
from utilities.security import SystemSecurity
from sqlalchemy.exc import SQLAlchemyError
import logging
import os

SYSTEM_PATH = os.getcwd()
JSON_FILE_PATH = "assets/azam_marines_flow.json"
JSON_FILE = os.path.join(SYSTEM_PATH, JSON_FILE_PATH)

flows_router = APIRouter()
security = SystemSecurity()

logger = logging.getLogger(__name__)


@flows_router.post("/create")
async def create_flow(flow_name: str, verify: bool = Depends(security.verify_api_key)):
    try:
        flow = FlowData.get_all()
        if flow:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="FLOW ALREADY EXISTS",
            )

        created_flow_id = WhatsappFlowsMiddleware.create_flow(flow_name)
        if not created_flow_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="FLOW CREATION FAILED",
            )

        _flow_data = FlowDataSchema(flow_name=flow_name, flow_id=created_flow_id)
        flow_data = _flow_data.dict(exclude_unset=True)
        flow_data = FlowData(**flow_data)
        flow_data.save()

        return JSONResponse(
            content=created_flow_id, status_code=status.HTTP_201_CREATED
        )

    except SQLAlchemyError as e:
        logger.error(f"Database error during flow creation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Unexpected error during flow creation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@flows_router.post("/upload")
async def upload_flow_json(
    verify: bool = Depends(security.verify_api_key),
):
    try:
        flow = FlowData.first_data()
        if not flow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="FLOW NOT FOUND, PLEASE CREATE A FLOW FIRST",
            )
        if flow.is_uploaded:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="FLOW ALREADY UPLOADED",
            )

        response = WhatsappFlowsMiddleware.upload_flow_json(flow.flow_id, JSON_FILE)
        if not response:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"FLOW UPLOAD FAILED, VERIFY YOUR FLOW ID OR FILE: {response}",
            )

        flow.is_uploaded = True
        flow.save()

        return JSONResponse(
            content=response,
            status_code=status.HTTP_200_OK,
        )

    except SQLAlchemyError as e:
        logger.error(f"Database error during flow upload: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Unexpected error during flow upload: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@flows_router.post("/publish")
async def publish_flow(verify: bool = Depends(security.verify_api_key)):
    try:
        flow = FlowData.first_data()
        if not flow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="FLOW NOT FOUND, PLEASE CREATE A FLOW FIRST",
            )
        if not flow.is_uploaded:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="FLOW NOT UPLOADED, PLEASE UPLOAD FIRST",
            )
        if flow.is_published:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="FLOW ALREADY PUBLISHED",
            )

        response = WhatsappFlowsMiddleware.publish_flow(flow.flow_id)
        if not response:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="FLOW PUBLISH FAILED",
            )

        flow.is_published = True
        flow.save()

        return JSONResponse(content=response, status_code=status.HTTP_200_OK)

    except SQLAlchemyError as e:
        logger.error(f"Database error during flow publish: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Unexpected error during flow publish: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@flows_router.post("/send")
async def send_flow(
    recipient_phone_number: str,
    verify: bool = Depends(security.verify_api_key),
):
    try:
        flow = FlowData.first_data()
        if not flow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="FLOW NOT FOUND, PLEASE CREATE A FLOW FIRST",
            )
        if not flow.is_uploaded:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="FLOW NOT UPLOADED, PLEASE UPLOAD FIRST",
            )

        if flow.is_published:
            response = WhatsappFlowsMiddleware.send_published_flow(
                flow.flow_id, recipient_phone_number
            )
        else:
            response = WhatsappFlowsMiddleware.send_unpublished_flow(
                flow.flow_id, recipient_phone_number
            )

        if not response:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="FLOW SENDING FAILED",
            )

        return JSONResponse(content=response, status_code=status.HTTP_200_OK)

    except SQLAlchemyError as e:
        logger.error(f"Database error during flow send: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Unexpected error during flow send: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
