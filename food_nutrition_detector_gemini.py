"""
Food Calorie & Nutrition Detector (Gemini free-tier version)
----------------------------------------------------------------
Takes a food name (text) OR a food image, and returns estimated
calories and macronutrients. Detects and rejects non-food input.

Uses Google's Gemini API, which has a free tier (no credit card needed).

Setup:
    pip install google-generativeai --break-system-packages
    Get a free key at: https://aistudio.google.com/apikey
    $env:GOOGLE_API_KEY="your-key-here"      (PowerShell)

Run:
    python food_nutrition_detector_gemini.py
"""

import json
import os
import google.generativeai as genai

genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-3.7-flash")

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
    response = model.generate_content([SYSTEM_PROMPT, f"Input: {food_name}"])
    return _parse_response(response.text)


def check_food_image(image_path: str) -> dict:
    """Check a food shown in an image file (jpg/png)."""
    import PIL.Image
    img = PIL.Image.open(image_path)
    response = model.generate_content(
        [SYSTEM_PROMPT, "Identify this image and determine if it is food.", img])
    return _parse_response(response.text)


def _parse_response(text: str) -> dict:
    text = text.strip().replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"is_food": False, "reason": f"Could not parse model response: {text[:200]}"}


def print_result(result: dict):
    print("-" * 50)
    if not result.get("is_food"):
        print("NOT FOOD DETECTED")
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
    if not os.environ.get("GOOGLE_API_KEY"):
        print("ERROR: GOOGLE_API_KEY environment variable is not set.")
        print('Set it with: $env:GOOGLE_API_KEY="your-key-here"')
        raise SystemExit(1)

    print("Food Calorie & Nutrition Detector (Gemini)")
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
