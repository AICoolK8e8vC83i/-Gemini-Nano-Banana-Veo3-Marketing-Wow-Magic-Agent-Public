# pipeline_types.py
from typing import TypedDict

class PipelineState(TypedDict, total=False):
    prompt: str
    edit: bool
    enhanced_prompt: str
    video_path: str
    video_url: str
    image_path: str
    edited_image_path: str
    text: str
    voice: str
    audio_path: str
    upload_response: dict
    logs: list
