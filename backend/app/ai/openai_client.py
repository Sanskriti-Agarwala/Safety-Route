import os
from ai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def call_llm(prompt: str, model: str = "gpt-4", max_tokens: int = 1000, temperature: float = 0.7) -> str:
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error calling OpenAI API: {str(e)}"