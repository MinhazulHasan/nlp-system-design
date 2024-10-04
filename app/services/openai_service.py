import openai
GPT_MODEL = "gpt-4o"

def openai_response(prompt: str, model: str = GPT_MODEL):
    messages = [
        {"role": "system", "content": "You answer questions from the articles."},
        {"role": "user", "content": prompt},
    ]
    response = openai.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0
    )

    response_message = response.choices[0].message.content

    return response_message