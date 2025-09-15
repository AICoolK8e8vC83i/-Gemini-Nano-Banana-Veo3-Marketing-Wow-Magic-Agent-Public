import fal_client
from pipeline_types import PipelineState
import requests
from pathlib import Path
import base64
import mimetypes


def file_to_data_uri(path: str) -> str:
    """Convert a local file into a Data URI for Fal AI."""
    mime, _ = mimetypes.guess_type(path)
    if not mime:
        mime = "image/png"
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime};base64,{b64}"


def download_video(video_url: str, out_path: str):
    """Download video from Fal AI URL to a local file."""
    r = requests.get(video_url, stream=True)
    r.raise_for_status()
    with open(out_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    return str(out_path)


def on_queue_update(state):
    if hasattr(state, "logs") and state.logs:
        for log in state.logs:
            print(log["message"])


def veo3_image_to_video_node(state: PipelineState) -> PipelineState:
    """
    Call Fal AI Veo3 with a local image (as Data URI) and save output video.
    Returns state with 'video_path'.
    """
    image_path = state.get("image_path")
    if not image_path:
        raise ValueError("❌ Missing image_path in state for Veo3 node")

    # Convert to Data URI
    image_data_uri = file_to_data_uri(image_path)

    # Call Fal AI
    result = fal_client.subscribe(
        "fal-ai/veo3/fast/image-to-video",
        arguments={
            "prompt": state.get("prompt", "") + " | Cinematic ad style, dramatic lighting, zoom out, product focus",
            "image_url": image_data_uri,
            "audio": False  # 🔑 disable Veo3's default audio
        },
        with_logs=True,
        on_queue_update=on_queue_update,
    )

    # Correct schema: top-level "video" dict
    if "video" not in result or "url" not in result["video"]:
        raise ValueError(f"❌ Unexpected Fal AI result format: {result}")

    video_url = result["video"]["url"]

    # Save locally
    output_dir = Path("demo/outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    local_video = output_dir / "veo3_video.mp4"
    download_video(video_url, str(local_video))

    print(f"✅ Veo 3 video saved locally: {local_video}")
    return {**state, "video_path": str(local_video)}

# ✅ Standalone test
if __name__ == "__main__":
    # Only include fields that PipelineState expects, with correct types
    test_state = {
        "image_path": "demo/outputs/edited_generated_image_edit.png",
        "prompt": "A sleek, futuristic electric car with a signature logo"
    }
    # If PipelineState requires other fields, add them here with correct types
    pipeline_state = PipelineState(image_path=test_state["image_path"], prompt=test_state["prompt"])
    print(veo3_image_to_video_node(pipeline_state))