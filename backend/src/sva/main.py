"""
Post method for a new video.
No streaming for now as we will process it in a asynchronous way for now.
Simply post it and then processing will be launched.
How do we known we finished processing the video ? Another endpoint.
It checks : do we finished processing the video. If yes, it returns the metadat
else an error.
"""

import logging
import time
import uuid

from fastapi import APIRouter, BackgroundTasks, FastAPI, HTTPException, status
from pydantic import BaseModel

logger = logging.getLogger(__name__)
app = FastAPI(title="Video Processing API", version="1.0.0")

v1_router = APIRouter()

# In-memory storage for demo purposes
video_status = {}
video_results = {}


class VideoRequest(BaseModel):
    """
    Represents the incoming data to process a video.
    """

    filename: str


class VideoResult(BaseModel):
    """
    Structure for returning video processing results.
    """

    duration: int
    resolution: str


def _process_video(video_id: str):
    """Simulate a long-running video processing task."""
    logger.info({"video_id": video_id, "state": "PROCESSING"})
    video_status[video_id] = "processing"
    # TODO: replace by real computation
    time.sleep(3)
    video_results[video_id] = {"duration": 120, "resolution": "1080p"}
    video_status[video_id] = "completed"
    logger.info({"video_id": video_id, "state": "COMPLETED"})


@v1_router.post("/videos", status_code=status.HTTP_202_ACCEPTED)
async def create_video(video: VideoRequest, background_tasks: BackgroundTasks):
    """
    Queue a video for processing. Returns a unique video_id to check status later.
    """
    video_id = str(uuid.uuid4())
    video_status[video_id] = "queued"
    logger.info({"video_id": video_id, "state": "QUEUED"})
    background_tasks.add_task(_process_video, video_id)
    return {"video_id": video_id, "status": "queued"}


@v1_router.get("/videos/{video_id}")
async def get_video(video_id: str):
    """
    Retrieve the processing status/results for a given video_id.
    Returns 404 if not found, or 202 if still processing.
    """
    if video_id not in video_status:
        logger.info({"video_id": video_id, "status": "NOT_FOUND_ERROR"})
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Video not found."
        )

    current_status = video_status[video_id]
    if current_status in ("queued", "processing"):
        logger.info({"video_id": video_id, "status": "STILL_PROCESSING"})
        raise HTTPException(
            status_code=status.HTTP_202_ACCEPTED,
            detail=f"Video is still {current_status}.",
        )

    logger.info({"video_id": video_id, "status": "FINISHED_PROCESSING"})
    return {
        "video_id": video_id,
        "status": current_status,
        "results": video_results[video_id],
    }


# Include v1 zfoutes under the /v1 prefix
app.include_router(v1_router, prefix="/v1", tags=["v1"])
