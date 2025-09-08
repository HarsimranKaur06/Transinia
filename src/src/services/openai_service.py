from openai import OpenAI
from src.config.settings import settings

_client = OpenAI(api_key=settings.openai_api_key)

def chat_5_8_sentences(system: str, user: str) -> str:
    resp = _client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": user}],
        temperature=0.2,
    )
    return resp.choices[0].message.content.strip()
