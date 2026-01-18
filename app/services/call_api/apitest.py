from openai import OpenAI
from google import genai
import traceback
import time
from app.core.globals import *

def test_api(usemodel, api_key, user_logger=None):
    for i in range(ATTEMP):
        try:
            msg = None
            if 'GPT' in usemodel.upper():
                client = OpenAI(api_key=api_key)
                msg = None
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "user", "content": "Hello"}
                    ],
                    max_completion_tokens=100
                )
                msg = response.choices[0].message.content  
                
            elif "GEMINI" in usemodel.upper():
                client = genai.Client(api_key=api_key)

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents="Hello",
                    config={
                        "max_output_tokens": 100
                    }
                )

                msg = None
                if response.candidates:
                    parts = response.candidates[0].content.parts
                    if parts and hasattr(parts[0], "text"):
                        msg = parts[0].text
                
            elif "GROK" in usemodel.upper():
                client = OpenAI(api_key=api_key)
                response = client.chat.completions.create(
                    model="grok-3-mini",
                    messages=[
                        {"role": "user", "content": "Hello"}
                    ],
                    max_completion_tokens=100
                )
                msg = response.choices[0].message.content

        except Exception as e:
            if user_logger:
                tb = traceback.format_exc()
                user_logger.log(f"[Attempt {i+1}] Error:\n{tb}")
                user_logger.log(f"[Attempt {i+1}] {e}")
            msg = None
            time.sleep(1)
            continue

        if msg:
            return True
        else:
            time.sleep(1)
            continue

    return False 