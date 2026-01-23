"""
AI MODEL INTEGRATION SERVICE
--------------------------
This file provides the interface to OpenAI's language models.
Specifically, it:

1. Initializes the connection to OpenAI using the API key
2. Provides the chat_5_8_sentences() function which:
   - Takes system instructions and user input
   - Sends them to the GPT-4o-mini model
   - Sets appropriate parameters for reliable outputs
   - Returns the AI-generated response

This service abstracts away the details of API communication and
parameter settings, making it easy to use AI capabilities throughout
the application.
"""

from openai import OpenAI
from backend.src.config.settings import settings

_client = OpenAI(api_key=settings.openai_api_key)

def chat_5_8_sentences(system: str, user: str, temperature: float = 0.2) -> str:
    resp = _client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": user}],
        temperature=temperature,
    )
    return resp.choices[0].message.content.strip()
