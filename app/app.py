import gradio as gr
from pathlib import Path
import time

from orchestrator import Orchestrator, concat_videos
from pipeline_types import PipelineState


def generate_ads(base_prompt: str, base_text: str):
    orch = Orchestrator()

    variations = [
        {"style": "Futuristic neon city backdrop", "voice": "Jessica"},
        # {"style": "Minimalist luxury showroom", "voice": "Brian"},
        {"style": "Rugged desert off-road adventure", "voice": "Aria"},
        # {"style": "Rainy night cinematic vibe", "voice": "Michael"},
        # {"style": "Bright corporate tech ad", "voice": "Sophia"},
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
    final_reel = concat_videos(video_outputs, "demo/outputs/final_reel.mp4")
    return final_reel, video_outputs


# === Gradio UI ===
with gr.Blocks() as demo:
    gr.Markdown("## 🚀 AI Marketing Ad Generator (End-to-End Pipeline)")

    with gr.Row():
        base_prompt = gr.Textbox(
            label="🎨 Base Image Prompt",
            value="Draw a stylish, photorealistic electric car with a signature logo"
        )
        base_text = gr.Textbox(
            label="📝 Base Voiceover Text",
            value="Introducing the future of driving. Sleek. Electric. Powerful."
        )

    generate_btn = gr.Button("🎬 Generate Ads")

    output_reel = gr.Video(label="Final Reel")
    output_gallery = gr.File(
        label="Individual Ads (MP4s)",
        type="filepath",
        file_types=[".mp4"],
        file_count="multiple"
    )

    generate_btn.click(
        fn=generate_ads,
        inputs=[base_prompt, base_text],
        outputs=[output_reel, output_gallery]
    )


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
