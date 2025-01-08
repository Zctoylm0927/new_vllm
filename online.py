from openai import OpenAI

# Initialize the client
openai_api_key = "EMPTY"
openai_api_base = "http://localhost:8000/v1"

client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)


def get_agent_response(user_input):
    """Send user input to the agent and get the response."""
    chat_response = client.chat.completions.create(
        model="Qwen/Qwen2.5-3B",
        messages=[
            {"role": "system", "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."},
            {"role": "user", "content": user_input},
        ],
        temperature=0.7,
        top_p=0.8,
        max_tokens=512,
    )
    return chat_response.choices[0].message.content


def main():
    """Read multi-line input until '<end>' and get agent response."""
    print("Welcome to Qwen Assistant! Type '<end>' to send your message or 'exit' to quit.")
    while True:
        buffer = []
        print("Enter your message (type '<end>' on a new line to send):")
        while True:
            line = input()
            if line.strip() == '<end>':
                break
            if line.strip().lower() in ['exit', 'quit']:
                print("Goodbye!")
                return
            buffer.append(line)
        user_input = '\n'.join(buffer)
        if not user_input.strip():
            print("Please enter a valid message.")
            continue
        reply = get_agent_response(user_input)
        print(f"Qwen: {reply}\n")


if __name__ == "__main__":
    main()
