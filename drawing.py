import os
import requests
import base64
from dotenv import load_dotenv

load_dotenv()

def generate_drawing_with_stability(prompt):
    stability_api_key = os.getenv("STABILITY_API_KEY")
    if not stability_api_key:
        return None, "Missing STABILITY_API_KEY"

    try:
        response = requests.post(
            "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
            headers={
                "Authorization": f"Bearer {stability_api_key}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            json={
                "text_prompts": [{"text": prompt}],
                "cfg_scale": 7,
                "height": 1152,
                "width": 896,
                "samples": 1,
                "steps": 30
            },
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("artifacts"):
                base64_image = data["artifacts"][0]["base64"]
                return base64.b64decode(base64_image), None
            else:
                return None, "No image returned"
        else:
            return None, f"API error {response.status_code}: {response.text}"

    except Exception as e:
        return None, f"Exception: {str(e)}"
