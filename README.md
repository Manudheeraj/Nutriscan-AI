# NutriScan AI

AI-powered food recognition and nutrition estimator. Describe a food in text, upload a photo, or use your camera — NutriScan identifies it and returns estimated calories and macronutrients. Non-food input is explicitly detected and rejected instead of producing a fake result.

## What it demonstrates
- **Multimodal AI input**: the same pipeline accepts a text description, an uploaded image, or a live camera photo
- **Structured output generation**: the model is prompted to return strict JSON so the app can reliably parse and display results
- **Input validation / guardrails**: explicitly checks whether the input is actually food before showing nutrition data, rather than hallucinating numbers for non-food input
- **A real web interface**: built with Streamlit, not just a CLI script

## How it works
1. User provides a food description, an uploaded photo, or a camera photo
2. The input is sent to Google's Gemini API with a system prompt that requires a strict JSON response shape
3. Gemini classifies whether the input is food, and if so, estimates nutrition for a typical serving
4. The app parses the JSON and displays either a nutrition breakdown or a clear "not food" message

## Setup
```bash
pip install google-generativeai pillow streamlit --break-system-packages
```
Get a free API key at https://aistudio.google.com/apikey (no credit card required)

Set it in your terminal:
```bash
# Windows PowerShell
$env:GOOGLE_API_KEY="your-key-here"

# Mac/Linux
export GOOGLE_API_KEY="your-key-here"
```

## Run
```bash
python -m streamlit run app.py
```
This opens the web interface in your browser at `localhost:8501`.

A command-line version (`food_nutrition_detector_gemini.py`) is also included for quick testing without the web UI.

## Example
- Input: `pizza` → returns calories, protein, carbs, and fat for a typical slice
- Input: `laptop` → returns "Not food detected" instead of fabricated nutrition data
- Input: a photo of a meal → identifies the dish and estimates its nutrition

## Known limitation / next steps
Nutrition values are currently *estimated* by the model from its general knowledge, not pulled from a verified nutrition database. A production version would use the AI model for food identification, then call a verified nutrition API (e.g. USDA FoodData Central) to fetch accurate values — separating "what is this" (the AI's job) from "what are the exact numbers" (a trusted data source's job).

## Built with
Python, Google Gemini API, Streamlit, Pillow