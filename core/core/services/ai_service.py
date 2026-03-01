import ollama

def ask_ai(message):
    response = ollama.chat(
        model="llama3",
        messages=[
            {"role": "system", "content": "You are a helpful study tutor. Explain in simple words."},
            {"role": "user", "content": message}
        ]
    )

    return response["message"]["content"]
