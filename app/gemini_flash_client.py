from pipeline_types import PipelineState
from google import genai
from dotenv import load_dotenv
import os 

load_dotenv()

def gemini_prompt_enhancer(state: PipelineState) -> PipelineState:
    """
    LangGraph-compatible wrapper around Gemini prompt enhancer.
    Expects:
        - state["prompt"]: str
        - state["edit"]: bool (optional, defaults False)
    Returns:
        {"enhanced_prompt": str}
    """
    prompt = state.get("prompt")
    if prompt is None:
        raise ValueError('"prompt" key is required in the state dictionary')
    
    edit = state.get("edit", False)

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("❌ GEMINI_API_KEY not set in environment or .env file")

    client = genai.Client(api_key=api_key)

    if edit:
        # Editing mode: FORCE drastic divergence + add logo/branding polish
        prompt = (
            f"REIMAGINE and TRANSFORM this image drastically. "
            f"Apply bold visual changes, cinematic lighting, and futuristic polish. "
            f"Make the edit obvious, visible, and impossible to miss. "
            f"Integrate imaginary premium brand logos, abstract symbols, or holographic emblems "
            f"to make it look like a high-end marketing ad. "
            f"Focus on color harmony, sleek branding placement, and wow-factor composition. "
            f"The previous enhanced prompt was: {prompt}"
        )
    else:
        # First-pass enhancement: immersive + brand polish
        prompt = (
            f"Enhance the prompt with state-of-the-art styling, immersive detail, "
            f"cinematic themes, and a high-quality 'wow' factor. "
            f"Integrate subtle branding cues (imaginary logo, futuristic symbol, or embossed mark) "
            f"to make it feel like a luxury ad campaign. "
            f"Prompt: {prompt}"
        )
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    enhanced_prompt = response.text if response.text else ""
    print(f"Enhanced Prompt: {enhanced_prompt}")

    return {**state, "enhanced_prompt": enhanced_prompt}


# ✅ Standalone test
if __name__ == "__main__":
    test_state = {"prompt": "Draw a stylish, photorealistic electric car with a signature logo", "edit": True}
    pipeline_state = PipelineState(**test_state)
    print(gemini_prompt_enhancer(pipeline_state))
