from openai import OpenAI
import time
# Set OpenAI's API key and API base to use vLLM's API server.
openai_api_key = "EMPTY"
openai_api_base = "http://localhost:8000/v1"

client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)
def get_ttft(content: str):
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
        stream=True,
    )

    for chunk in chat_response:
        ttft = time.time() - start_time
        break

    chat_response.close()
    return ttft