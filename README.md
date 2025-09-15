# 🚀 Gemini 2.5 Nano Flash — Multi-Ad Generator (E2E)

**Demo Link:** [Watch Demo](https://www.veed.io/view/f01083cc-5879-4e21-b33b-33aa18693866?source=editor&panel=share)  

---

## 📌 Overview
This project is an **end-to-end multi-ad creative generator pipeline**, built with **Gemini 2.5 Nano Flash** and **Veo 3**.  
It takes a simple product prompt (e.g. *“Stylish electric car with a signature logo”*) and outputs **fully produced ad videos** with:  

- **Ad copy** (Gemini Flash)  
- **Photorealistic images** (Gemini Nano → image gen + editing)  
- **Video generation** (Veo 3 image-to-video)  
- **Voiceovers** (ElevenLabs TTS)  
- **Final merged ads** with music/voice + visuals (FFmpeg)  
- **Gradio dashboard** for interactive ad generation and preview  

The result: a production-ready ad pipeline that can spin up **multiple variations** for A/B testing in minutes.  

---

## ✨ Features
- 🖼️ Text → Image generation (Gemini Nano Flash)  
- 🎬 Image → Cinematic video (Veo 3)  
- 🎙️ Voice-over narration (ElevenLabs)  
- 🔗 Automatic video+audio merging (FFmpeg)  
- 📊 Multi-ad generation & final reel concatenation  
- 🌐 Gradio dashboard for user-friendly control  

---

## ⚙️ Architecture

```mermaid
flowchart LR
    A[Prompt Input] --> B[Gemini Flash Prompt Enhancer]
    B --> C[Gemini Nano Text-to-Image]
    C -->|Conditional: Edit?| D[Gemini Nano Image Editing]
    C -->|Else| E[Veo 3 Image-to-Video]
    D --> E
    E --> F[ElevenLabs TTS]
    F --> G[FFmpeg Merge]
    G --> H[Final Ad Output]
    H --> I[Concat Reel (Optional)]
