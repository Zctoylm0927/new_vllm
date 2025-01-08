from openai import OpenAI
# Set OpenAI's API key and API base to use vLLM's API server.
openai_api_key = "EMPTY"
openai_api_base = "http://localhost:8000/v1"

client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)
def get_length_request(len):
    chat_response = client.chat.completions.create(
        model="Qwen/Qwen2.5-3B",
        messages=[
            {"role": "system", "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."},
            {"role": "user", "content": "Generate a problem of strict length " + str(len)},
        ],
        temperature=0.7,
        top_p=0.8,
        max_tokens=512,
    )
    return chat_response.choices[0].message.content