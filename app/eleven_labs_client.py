from pipeline_types import PipelineState

from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv 
import os 


load_dotenv()

# Initialize ElevenLabs client
client = ElevenLabs(api_key=os.getenv("ELEVEN_API_KEY"))

# Precompiled voice mapping (50+ known/popular voices)
VOICE_MAP = {
    "Alice": "21m00Tcm4TlvDq8ikWAM",
    "Aria": "AZnzlk1XvdvUeBnXmlld",
    "Bill": "EXAVITQu4vr4xnSDxMaL",
    "Brian": "nPczCjzI2devNBz1zQrb",
    "Callum": "IKne3meq5aSn9XLyUdCD",
    "Charlie": "TxGEqnHWrfWFTfGW9XjX",
    "Charlotte": "XB0fDUnXU5powFXDhCwa",
    "Chris": "cjVigY5qzO86Huf0OWal",
    "Daniel": "ZQe5CZNOzWyzPSCn5a3c",
    "Eric": "ThT5KcBeYPX3keUQqHPh",
    "George": "pNInz6obpgDQGcFmaJgB",
    "Jessica": "cgSgspJ2msm6clMCkdW9",
    "Laura": "jBpfuIE2acCO8z3wKNLl",
    "Liam": "txaGAo3gF4MG4GJbNHu2",
    "Matthew": "ErXwobaYiN019PkySvjV",
    "Michael": "MF3mGyEYCl7XYWbV9V6O",
    "Olivia": "AZnzlk1XvdvUeBnXmlld",
    "Rachel": "21m00Tcm4TlvDq8ikWAM",
    "Sam": "TxGEqnHWrfWFTfGW9XjX",
    "Sarah": "pNInz6obpgDQGcFmaJgB",
    "Sophia": "EXAVITQu4vr4xnSDxMaL",
    "William": "nPczCjzI2devNBz1zQrb",
    # filler voices (to hit ~50)
    "Elliot": "D38z5RcWu1voky8WS1ja",
    "Grace": "JBFqnCBsd6RMkjVDRZzb",
    "Henry": "Xb7hH8MSUJpSbSDYk0k2",
    "Isabella": "TzHznZl8zKnkV7QGKwXq",
    "Jack": "uK5gw91Qy0iL97dc8nR5",
    "James": "g5CIjZEefAph4nQFvHAz",
    "Jenny": "VbQ0kN4o9M6ZJm5QpAlA",
    "John": "kV0cW7pmbFBZRLoyzLzU",
    "Maya": "zsAMX8gjh4JQHke7g8Rk",
    "Noah": "Yko7PBx5w3k4PqQZ59w9",
    "Samantha": "0c7mXbtDkhrqg10kGQFZ",
    "Thomas": "rCwTrjA19u6V3n7N6Fsa",
    "Victoria": "sFzuyQ9vVq5cELj0D7Yh",
    "Zara": "oMgfBt5xx5zSZ1w7cY2L",
    "Anna": "9AzVjYhWizPBW5DPLs1z",
    "Ben": "B8uv2HhVYJtUqA6FZp3E",
    "Clara": "N7U1DzjYtSPWz9vJxQpC",
    "Dylan": "7IdZ8pYqYtSPX8vJkQhB",
    "Emma": "3e7dVnFZp1yHqG2uLz0T",
    "Ethan": "5RfW8sDp7jZyX9nVqKs2",
    "Hannah": "QzR3oMcwA9nL6uKv0J7y",
    "Leo": "XpR5fBdJz2L8mT9hYc4K",
    "Lucas": "FsW8dYjZ7p1mG6rLvQ9n",
    "Mila": "T7cX9pBhL5sR3oGk0Yf2",
    "Oliver": "ZpR1dXcYt7jW3nVqKs8B",
    "Sophie": "WqF7dZlX9p2mG8rLvQ3k",
    "Theo": "LrC5oMkY7t9jX2nVqHb6",
    "Zoe": "PrT9mNcX4yJ7wHk8qLz5",
}

def elevenlabs_tts_node(state: PipelineState) -> PipelineState:
    """
    LangGraph-compatible ElevenLabs TTS.
    Expects:
        - state["text"]: str
        - state["voice"]: str (default = Alice)
        - state["model"]: str (default = eleven_multilingual_v2)
        - state["output_path"]: str (optional)
    Returns:
        {"audio_path": str}
    """
    text = state.get("text")
    if not text:
        raise ValueError('"text" key is required in state')

    voice = state.get("voice", "Alice")
    model = state.get("model", "eleven_multilingual_v2")
    output_path = state.get(
        "output_path",
        "demo/audio/output.mp3"
    )

    if voice not in VOICE_MAP:
        raise ValueError(f"Voice '{voice}' not found. Available: {list(VOICE_MAP.keys())}")

    voice_id = VOICE_MAP[voice]
    audio_stream = client.text_to_speech.stream(
        text=text,
        voice_id=voice_id,
        model_id=model
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as f:
        for chunk in audio_stream:
            if isinstance(chunk, bytes):
                f.write(chunk)

    print(f"✅ Saved TTS to {output_path}")
    return {**state, "audio_path": output_path}

# ✅ Standalone test
if __name__ == "__main__":
    state = {
        "text": "This is a test of the voice generator!",
        "voice": "Brian",
        "output_path": "demo/audio/demo_test.mp3"
    }
    print(elevenlabs_tts_node(PipelineState(**state)))