"""
Food Calorie & Nutrition Detector
-----------------------------------
Takes a food name (text) OR a food image, and returns estimated
calories and macronutrients. Detects and rejects non-food input.

Setup:
    pip install anthropic --break-system-packages
    export ANTHROPIC_API_KEY="your-key-here"   (get one free at console.anthropic.com)

Run:
    python food_nutrition_detector.py
"""

import base64
import json
import os
from anthropic import Anthropic

client = Anthropic()  # reads ANTHROPIC_API_KEY from environment

SYSTEM_PROMPT = """You are a food identification and nutrition estimation assistant.
Given input (a text description or an image), determine if it depicts or names an
actual food or drink item.

Respond with ONLY raw JSON, no markdown fences, no preamble, matching exactly this shape:

If it IS food:
{"is_food": true, "food_name": "...", "serving_size": "...", "calories": number, "protein_g": number, "carbs_g": number, "fat_g": number}

If it is NOT food (an object, animal, person, blank image, random text, etc.):
{"is_food": false, "reason": "short explanation of what it actually is"}

Use reasonable typical estimates for a standard serving. Output nothing but the JSON object.
"""


def check_food_text(food_name: str) -> dict:
    """Check a food described as plain text."""
    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": food_name}],
    )
    return _parse_response(message)


def check_food_image(image_path: str) -> dict:
    """Check a food shown in an image file (jpg/png)."""
    with open(image_path, "rb") as f:
        image_data = base64.standard_b64encode(f.read()).decode("utf-8")

    media_type = "image/jpeg" if image_path.lower().endswith((".jpg", ".jpeg")) else "image/png"

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=500,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data,
                        },
                    },
                    {"type": "text", "text": "Identify this and determine if it is food."},
                ],
            }
        ],
    )
    return _parse_response(message)


def _parse_response(message) -> dict:
    text = message.content[0].text.strip()
    text = text.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"is_food": False, "reason": f"Could not parse model response: {text[:200]}"}


def print_result(result: dict):
    print("-" * 50)
    if not result.get("is_food"):
        print(f"NOT FOOD DETECTED")
        print(f"Reason: {result.get('reason', 'Unknown')}")
    else:
        print(f"Food: {result.get('food_name')}")
        print(f"Serving size: {result.get('serving_size')}")
        print(f"Calories: {result.get('calories')} kcal")
        print(f"Protein: {result.get('protein_g')} g")
        print(f"Carbs:   {result.get('carbs_g')} g")
        print(f"Fat:     {result.get('fat_g')} g")
    print("-" * 50)


if __name__ == "__main__":
    print("Food Calorie & Nutrition Detector")
    print("Type a food name, or 'image:<path>' to check an image, or 'quit' to exit.\n")

    while True:
        user_input = input("Enter food name or image path: ").strip()
        if user_input.lower() in ("quit", "exit"):
            break
        if not user_input:
            continue

        if user_input.lower().startswith("image:"):
            path = user_input.split(":", 1)[1].strip()
            if not os.path.exists(path):
                print(f"File not found: {path}")
                continue
            result = check_food_image(path)
        else:
            result = check_food_text(user_input)

        print_result(result)
