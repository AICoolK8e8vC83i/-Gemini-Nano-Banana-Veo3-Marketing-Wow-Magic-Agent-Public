from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from pathlib import Path
import subprocess
import time

# === Import your nodes ===
from gemini_flash_client import gemini_prompt_enhancer
from gemini_nano_flash import gemini_nano_text_to_image, gemini_nano_image_editing
from eleven_labs_client import elevenlabs_tts_node
from veo3_client import veo3_image_to_video_node
from pipeline_types import PipelineState


# === FFmpeg merge node ===
def merge_image_audio_node(state: PipelineState) -> PipelineState:
    video_path = state.get("video_path")  # from Veo 3
    audio_path = state.get("audio_path")  # from ElevenLabs

    if not video_path or not audio_path:
        raise ValueError("❌ video_path or audio_path missing in state")

    output_dir = Path("demo/outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "final_ad.mp4"

    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-i", str(audio_path),
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-shortest", str(output_path)
    ]
    subprocess.run(cmd, check=True)

    print(f"✅ Final ad video with audio: {output_path}")
    return {**state, "video_path": str(output_path)}


# === Orchestrator Class ===
class Orchestrator:
    def __init__(self):
        self.graph = StateGraph(PipelineState)

        self.graph.add_node("prompt_enhancer", gemini_prompt_enhancer)
        self.graph.add_node("image_gen", gemini_nano_text_to_image)
        self.graph.add_node("image_edit", gemini_nano_image_editing)
        self.graph.add_node("tts", elevenlabs_tts_node)
        self.graph.add_node("veo3_video", veo3_image_to_video_node)
        self.graph.add_node("merge", merge_image_audio_node)

        # Flow
        self.graph.add_edge(START, "prompt_enhancer")
        self.graph.add_edge("prompt_enhancer", "image_gen")

        def maybe_edit(state: PipelineState):
            return "image_edit" if state.get("edit", False) else "veo3_video"

        # If editing → image_edit first, else go straight to Veo3
        self.graph.add_conditional_edges("image_gen", maybe_edit, ["image_edit", "veo3_video"])
        self.graph.add_edge("image_edit", "veo3_video")

        # Always go video → TTS → Merge
        self.graph.add_edge("veo3_video", "tts")
        self.graph.add_edge("tts", "merge")
        self.graph.add_edge("merge", END)

        self.app = self.graph.compile()

    def run(self, state: PipelineState) -> dict:
        return self.app.invoke(state)


# === Helper: merge multiple ads ===
def concat_videos(video_paths, output_path="demo/outputs/final_reel.mp4"):
    file_list_path = "demo/outputs/video_list.txt"
    with open(file_list_path, "w") as f:
        for vp in video_paths:
            f.write(f"file '{Path(vp).absolute()}'\n")

    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", file_list_path, "-c", "copy", output_path
    ]
    subprocess.run(cmd, check=True)
    print(f"✅ Reel created: {output_path}")
    return output_path


# === Standalone test with multiple ads ===
if __name__ == "__main__":
    orch = Orchestrator()

    base_prompt = "Draw a stylish, photorealistic electric car with a signature logo"
    base_text = "Introducing the future of driving. Sleek. Electric. Powerful."

    variations = [
        {"style": "Futuristic neon city backdrop", "voice": "Jessica"},
        {"style": "Rugged desert off-road adventure", "voice": "Aria"},
    ]

    video_outputs = []
    for i, var in enumerate(variations, 1):
        print(f"\n🎬 Generating Ad {i}: {var['style']}")

        state: PipelineState = {
            "prompt": f"{base_prompt} — Style: {var['style']}",
            "edit": False,
            "voice": var["voice"],
            "text": f"{base_text} | Theme: {var['style']}",
        }

        final_state = orch.run(state)
        video_path = final_state.get("video_path", f"demo/outputs/final_ad_v{i}.mp4")

        # Rename per variation
        new_path = Path(f"demo/outputs/final_ad_v{i}.mp4")
        Path(video_path).rename(new_path)
        video_outputs.append(str(new_path))
        time.sleep(3)

    # Merge all ads into one reel
    concat_videos(video_outputs, "demo/outputs/final_reel.mp4")
