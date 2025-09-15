from pipeline_types import PipelineState
from google import genai
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()

def gemini_nano_text_to_image(state: PipelineState) -> PipelineState:
    """
    LangGraph-compatible Gemini Nano text-to-image.
    Expects:
        - state["enhanced_prompt"] (preferred) or state["prompt"]
    Returns:
        {"image_path": str}
    """
    prompt = state.get("enhanced_prompt") or state.get("prompt")
    if not prompt:
        raise ValueError('"prompt" or "enhanced_prompt" key is required in state')

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("❌ GEMINI_API_KEY not set in environment or .env file")

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.5-flash-image-preview",
        contents=[prompt],
    )

    output_dir = Path("demo/outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = None

    for part in response.candidates[0].content.parts:
        if part.text:
            print(part.text)
        elif part.inline_data:
            image = Image.open(BytesIO(part.inline_data.data))
            output_path = output_dir / "generated_image.png"
            image.save(output_path)
            print(f"✅ Image saved: {output_path}")
            print(f"📁 Size: {output_path.stat().st_size} bytes")

    if not output_path:
        raise RuntimeError("❌ No image data returned from Gemini")

    return {"image_path": str(output_path)}


def gemini_nano_image_editing(state: PipelineState) -> PipelineState:
    """
    LangGraph-compatible Gemini Nano image editing.
    Expects:
        - state["edit_prompt"]: str (optional, defaults to enhanced_prompt)
        - state["image_path"]: str (from image_gen)
    Returns:
        {"edited_image_path": str}
    """
    prompt = state.get("edit_prompt") or state.get("enhanced_prompt")
    image_path = state.get("image_path")

    if not prompt or not image_path:
        raise ValueError('"enhanced_prompt" or "edit_prompt" plus "image_path" required in state')

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("❌ GEMINI_API_KEY not set in environment or .env file")

    client = genai.Client(api_key=api_key)
    image = Image.open(image_path)

    response = client.models.generate_content(
        model="gemini-2.5-flash-image-preview",
        contents=[prompt, image],
    )

    output_dir = Path("demo/outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "edited_generated_image_edit.png"

    for part in response.candidates[0].content.parts:
        if part.text:
            print(part.text)
        elif part.inline_data:
            image = Image.open(BytesIO(part.inline_data.data))
            image.save(output_path)
            print(f"✅ Edited image saved: {output_path}")
            print(f"📁 Size: {output_path.stat().st_size} bytes")

    return {"edited_image_path": str(output_path)}

if __name__ == "__main__":
    state1 = {"prompt": "A photorealistic sports drink with a bodybuilder"}
    print(gemini_nano_text_to_image(PipelineState(**state1)))

    state2 = {
        "edit_prompt": "Add a phone sync to the watch",
        "image_path": "demo/outputs/generated_image.png"
    }
    print(gemini_nano_image_editing(PipelineState(**state2)))
