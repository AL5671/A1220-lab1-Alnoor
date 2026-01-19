# gpt.py
import json
from openai import OpenAI

client = OpenAI()

CATEGORIES = ["Meals", "Transport", "Lodging", "Office Supplies", 
"Entertainment", "Other"]

def extract_receipt_info(image_b64):
    """Extract structured receipt fields from a base64-encoded receipt image.

    Sends the receipt image to the OpenAI API and requests a single JSON object
    containing: date, amount, vendor, and category.

    Args:
        image_b64: Base64-encoded JPEG image data (no data URL prefix).

    Returns:
        A dict with keys: "date", "amount", "vendor", and "category".
        Any field that cannot be determined will be None.

    Raises:
        json.JSONDecodeError: If the model response is not valid JSON.
        openai.OpenAIError: If the OpenAI API request fails.
    """
    prompt = f"""
You are an information extraction system.
Extract ONLY the following fields from the receipt image:

date: the receipt date as a string
amount: the total amount paid as it appears on the receipt
vendor: the merchant or vendor name
category: one of [{", ".join(CATEGORIES)}]

Return EXACTLY one JSON object with these four keys and NOTHING ELSE.
Do not include explanations, comments, or formatting.
Do not wrap the JSON in markdown.
If a field cannot be determined, use null.

The output must be valid JSON.
"""
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        seed=43,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_b64}"
                        }
                    }
                ]
            }
        ]
    )
    return json.loads(response.choices[0].message.content)

