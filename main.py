import time
import numpy as np
import os
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed
# Initialize OpenAI API client
openai_api_key = "EMPTY"
openai_api_base = "http://localhost:8000/v1"

client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)


def get_tpot(content: str, priority=0):
    """
    Measure the time to generate all tokens (Total Processing Time per Token - TPOT).
    """
    start_time = time.time()
    chat_response = client.chat.completions.create(
        model="Qwen/Qwen2.5-7B-Instruct",
        messages=[
            {"role": "system", "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."},
            {"role": "user", "content": content},
        ],
        temperature=0.7,
        top_p=0.8,
        max_tokens=4096,
        extra_body={
            "priority": 0
        }
    )

    total_time = time.time() - start_time
    complete_tokens = chat_response.usage.completion_tokens
    tpot = complete_tokens / total_time if total_time > 0 else float('inf')

    generated_response = chat_response.choices[0].message.content
    return tpot


def get_ttft(content: str, priority=0):
    """
    Measure the Time to First Token (TTFT) during streaming output.
    """
    start_time = time.time()
    chat_response = client.chat.completions.create(
        model="Qwen/Qwen2.5-7B-Instruct",
        messages=[
            {"role": "system", "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."},
            {"role": "user", "content": content},
        ],
        temperature=0.7,
        top_p=0.8,
        max_tokens=4096,
        stream=True,
        extra_body={
            "priority": 0
        }
    )

    for chunk in chat_response:
        ttft = time.time() - start_time
        break

    chat_response.close()
    return ttft


def generate_mixed_lengths(num_samples, weights, lambdas):
    """
    Generate text lengths using Poisson distributions.
    """
    if len(weights) != len(lambdas):
        raise ValueError("weights and lambdas must have the same length.")

    categories = np.random.choice(
        range(len(lambdas)), size=num_samples, p=weights)

    lengths = [np.random.poisson(lambdas[category]) for category in categories]
    return lengths


def response_fixed_length(target_len, mode="tpot"):
    """
    Select the closest file to the target length, use its content as the prompt,
    and measure either TTFT or TPOT depending on the mode.
    """
    current_dir = os.path.abspath(os.path.dirname(__file__))
    benchmark_dir = os.path.join(current_dir, "benchmark")

    files = [f for f in os.listdir(benchmark_dir) if f.startswith(
        "token_") and f.endswith(".in")]
    if not files:
        raise FileNotFoundError(
            "No valid .in files found in the benchmark directory.")

    token_files = {}
    for file in files:
        try:
            token_count = int(file.split('_')[1].split('.')[0])
            token_files[token_count] = file
        except ValueError:
            continue

    closest_token_count = min(
        token_files.keys(), key=lambda x: abs(x - target_len))
    closest_file = token_files[closest_token_count]

    file_path = os.path.join(benchmark_dir, closest_file)
    with open(file_path, 'r', encoding='utf-8') as f:
        prompt = f.read()

    if mode == "ttft":
        metric_value = get_ttft(prompt, priority=target_len)
    else:
        metric_value = get_tpot(prompt, priority=target_len)

    return metric_value


def _process_event(idx, event, start_sim_time, mode, all_events):
    scheduled_send_time, user_id, target_len = event
    now = time.time()
    time_elapsed = now - start_sim_time
    wait_time = scheduled_send_time - time_elapsed
    # print(wait_time)
    if wait_time > 0:
        time.sleep(wait_time)

    metric = response_fixed_length(target_len, mode=mode)
    if mode == "ttft":
        print(
            f"[{idx + 1}/{len(all_events)}] User {user_id} | target_len={target_len} | ttft = {metric:.4f}")
    else:
        print(
            f"[{idx + 1}/{len(all_events)}] User {user_id} | target_len={target_len} | tpot = {metric:.4f}")


def simulate_requests(mode, load_scenario):
    """
    Simulate requests from multiple users under different load scenarios.
    """
    scenario_configs = {
        "low": {
            "user_count": 8,
            "lambda_requests": 5,
            "lambda_frequency": 0.05,
            "weights": [0.5, 0.3, 0.15, 0.05],
            "length_lambdas": [20, 100, 2000, 15000]
        },
        "medium": {
            "user_count": 12,
            "lambda_requests": 10,
            "lambda_frequency": 0.2,
            "weights": [0.2, 0.3, 0.35, 0.15],
            "length_lambdas": [20, 100, 2000, 20000]
        },
        "high": {
            "user_count": 24,
            "lambda_requests": 10,
            "lambda_frequency": 0.4,
            "weights": [0.1, 0.2, 0.35, 0.35],
            "length_lambdas": [100, 1500, 5000, 30000]
        }
    }

    if load_scenario not in scenario_configs:
        raise ValueError(f"Unknown load_scenario: {load_scenario}")

    config = scenario_configs[load_scenario]
    user_count = config["user_count"]
    lambda_requests = config["lambda_requests"]
    lambda_frequency = config["lambda_frequency"]
    weights = config["weights"]
    length_lambdas = config["length_lambdas"]

    all_events = []
    user_ids = range(1, user_count + 1)

    for user_id in user_ids:
        user_request_count = np.random.poisson(lambda_requests)
        if user_request_count <= 0:
            continue

        lengths = generate_mixed_lengths(
            user_request_count, weights, length_lambdas)
        intervals = np.random.exponential(
            scale=1.0 / lambda_frequency, size=user_request_count)
        send_times = np.cumsum(intervals)

        for i in range(user_request_count):
            all_events.append((send_times[i], user_id, lengths[i]))

    all_events.sort(key=lambda x: x[0])

    start_sim_time = time.time()
    with ThreadPoolExecutor(max_workers=user_count) as executor:
        futures = []
        for idx, event in enumerate(all_events):
            futures.append(executor.submit(_process_event,
                                           idx,
                                           event,
                                           start_sim_time,
                                           mode,
                                           all_events))
        for future in as_completed(futures):
            _ = future.result()


if __name__ == "__main__":
    # response_fixed_length(20000)
    # response_fixed_length(5000)
    # exit(0)
    mode = "tpot"
    load_scenario = "high"

    print(
        f"Starting simulation with mode={mode}, load_scenario={load_scenario}...")
    simulate_requests(mode=mode, load_scenario=load_scenario)
