# Food Calorie & Nutrition Detector

A small AI tool that takes a food name (text) or a food photo (image) and returns
estimated calories and macronutrients — or clearly flags when the input isn't food
at all.

## What it demonstrates
- **Multimodal AI input**: accepts both text and image input to the same pipeline
- **Structured output generation**: forces the model to return strict JSON so the
  app can reliably parse and display results
- **Input validation / guardrails**: explicitly detects and rejects non-food input
  instead of guessing or hallucinating nutrition data for something that isn't food

## How it works
1. User provides either a food name or a photo
2. The input is sent to Claude with a system prompt that requires a strict JSON
   response shape
3. Claude classifies whether the input is food, and if so, estimates nutrition
   for a typical serving
4. The app parses the JSON and displays either the nutrition breakdown or a
   "not food" message

## Setup
```bash
pip install anthropic --break-system-packages
export ANTHROPIC_API_KEY="your-key-here"
python food_nutrition_detector.py
```
Get a free API key at https://console.anthropic.com

## Example usage
```
Enter food name or image path: banana
--------------------------------------------------
Food: Banana
Serving size: 1 medium banana (118g)
Calories: 105 kcal
Protein: 1.3 g
Carbs:   27 g
Fat:     0.4 g
--------------------------------------------------

Enter food name or image path: laptop
--------------------------------------------------
NOT FOOD DETECTED
Reason: A laptop is an electronic device, not a food item.
--------------------------------------------------

Enter food name or image path: image:my_lunch.jpg
--------------------------------------------------
Food: Grilled chicken sandwich
...
```

## Known limitation / next steps
Nutrition values are currently *estimated* by the model from its general
knowledge, not pulled from a verified nutrition database. A production version
would use Claude for food identification, then call a verified nutrition API
(e.g. USDA FoodData Central) to fetch accurate values — separating
"what is this" (AI's job) from "what are the exact numbers" (a trusted data
source's job).
