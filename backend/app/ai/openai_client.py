from openai import OpenAI
from app.core.config import get_settings

settings = get_settings()

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def call_llm(prompt: str, model: str = "gpt-4", max_tokens: int = 500) -> str:
    """
    Call OpenAI API with a prompt.
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return ""