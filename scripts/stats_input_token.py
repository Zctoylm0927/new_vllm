import os
import time
from openai import OpenAI
import time
# Set OpenAI's API key and API base to use vLLM's API server.
openai_api_key = "EMPTY"
openai_api_base = "http://localhost:8000/v1"

client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)


def get_prompt_tokens(content: str):
    start_time = time.time()
    chat_response = client.chat.completions.create(
        model="Qwen/Qwen2.5-3B",
        messages=[
            {"role": "system", "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."},
            {"role": "user", "content": content},
        ],
        temperature=0.7,
        top_p=0.8,
        max_tokens=512,
    )

    total_time = time.time() - start_time
    prompt_tokens = chat_response.usage.prompt_tokens
    return prompt_tokens


def process_files():
    directory = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "../benchmark"))

    if not os.path.exists(directory):
        print(f"Directory {directory} does not exist.")
        return

    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)

        if filename.endswith(".in") and not filename.startswith("token_") and os.path.isfile(filepath):
            with open(filepath, "r", encoding="utf-8") as file:
                content = file.read()

            prompt_tokens = get_prompt_tokens(content)

            new_filename = f"token_{prompt_tokens}.in"
            new_filepath = os.path.join(directory, new_filename)

            os.rename(filepath, new_filepath)
            print(f"Renamed {filename} to {new_filename}")


if __name__ == "__main__":
    process_files()
