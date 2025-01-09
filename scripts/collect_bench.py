import os
import shutil
from termcolor import colored
import sys
import numpy as np


def sample_test():
    lambda_tokens = 10

    samples = np.random.poisson(lam=lambda_tokens, size=100)
    for i, sample in enumerate(samples):
        print(f"Sample {i + 1}: {sample}")

    mean = np.mean(samples)
    variance = np.var(samples)

    print(f"\nMean: {mean}")
    print(f"Variance: {variance}")


def exponential_test():
    # Rate parameter (λ), which is the inverse of the mean (1/mean)
    lambda_rate = 0.05

    # Generate 100 samples from an exponential distribution
    samples = np.random.exponential(scale=1/lambda_rate, size=100)
    for i, sample in enumerate(samples):
        # Format to 4 decimal places for better readability
        print(f"Sample {i + 1}: {sample:.4f}")

    # Calculate the mean and variance of the samples
    mean = np.mean(samples)
    variance = np.var(samples)

    print(f"\nMean: {mean:.4f}")
    print(f"Variance: {variance:.4f}")


def compare_token_counts():
    """Compare actual token counts with estimated values in file names."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    target_folder = os.path.join(script_dir, "../benchmark")

    if not os.path.exists(target_folder):
        print("Benchmark directory does not exist.")
        return

    for file in os.listdir(target_folder):
        if file.startswith('token_') and file.endswith('.in'):
            file_path = os.path.join(target_folder, file)

            # Extract the token count from the file name
            try:
                filename_token = int(file.split('_')[1].split('.')[0])
            except (IndexError, ValueError):
                print(f"Invalid file name format: {file}")
                continue

            # Compute actual tokens using the provided function
            actual_tokens = estimate_tokens_from_words(file_path)

            # Print results with color coding
            actual_tokens_colored = colored(f"{actual_tokens}", "red")
            filename_token_colored = colored(f"{filename_token}", "green")
            print(
                f"Stats Tokens: {actual_tokens_colored}, Actual Tokens: {filename_token_colored}, Rate: {filename_token*1.0/actual_tokens}")


def estimate_tokens_from_words(file_path):
    """Estimate token count from the file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    return len(text.split())


def collect_code_with_prompt(source_folder, max_tokens=15000):
    """Collect code files with token count <= max_tokens, convert to .in with a prompt."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    target_folder = os.path.join(script_dir, "../benchmark")
    os.makedirs(target_folder, exist_ok=True)

    for root, _, files in os.walk(source_folder):
        for file in files:
            if file.endswith(('.c', '.cpp', '.py')):  # Check file extensions
                file_path = os.path.join(root, file)
                tokens = estimate_tokens_from_words(file_path)

                if tokens == 0:
                    print(f"Skipped (empty file): {file_path}")
                    continue

                print(f"File: {file_path}, Tokens: {tokens}")
                if tokens <= max_tokens:
                    # Prepare target file name by replacing the extension with .in
                    new_file_name = os.path.splitext(file)[0] + ".in"
                    target_path = os.path.join(target_folder, new_file_name)

                    # Read and modify content
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    content += "\n\nplease explain the details of the code above.\n"

                    # Write modified content to the new .in file
                    with open(target_path, 'w', encoding='utf-8') as f:
                        f.write(content)

                    print(f"Processed and saved as: {target_path}")
                else:
                    print(f"Skipped (too many tokens): {file_path}")


def clear_all_code_files():
    """Clear all code files in ../benchmark."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    target_folder = os.path.join(script_dir, "../benchmark")
    if os.path.exists(target_folder):
        for file in os.listdir(target_folder):
            if not file.endswith('.in'):
                file_path = os.path.join(target_folder, file)
                os.remove(file_path)
                print(f"Deleted: {file_path}")
    else:
        print("Target folder does not exist.")


def clear_non_token_files():
    """Clear non-token_*.in files in ../benchmark."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    target_folder = os.path.join(script_dir, "../benchmark")
    if os.path.exists(target_folder):
        for file in os.listdir(target_folder):
            if file.endswith('.in') and not file.startswith('token_'):
                file_path = os.path.join(target_folder, file)
                os.remove(file_path)
                print(f"Deleted: {file_path}")
    else:
        print("Target folder does not exist.")


def process_in_files():
    # Locate the benchmark directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    benchmark_dir = os.path.join(script_dir, "../benchmark")

    # Check if the directory exists
    if not os.path.exists(benchmark_dir):
        print("Benchmark directory does not exist.")
        return

    # Process all .in files
    for file in os.listdir(benchmark_dir):
        if file.endswith('.in'):
            file_path = os.path.join(benchmark_dir, file)

            # Read the file content
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Check if the last line is the specific text and remove it
            if lines and lines[-1].strip() == "please explain the details of the code above.":
                lines = lines[:-1]  # Remove the last line

            # Add the new instruction at the beginning
            new_instruction = (
                "please explain the details of the code as follows and implement a more complex scenario "
                "based on the following code. Ensure that the code for the implemented scenario is as long as possible.\n"
            )
            lines.insert(0, new_instruction)

            # Write the updated content back to the file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)

            print(f"Processed file: {file_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script_name.py <mode> [arguments]")
        sys.exit(1)

    mode = sys.argv[1].lower()

    if mode == "collect":
        if len(sys.argv) < 3:
            print("Usage: python script_name.py collect <source_folder>")
            sys.exit(1)
        source_folder = sys.argv[2]
        collect_code_with_prompt(source_folder)

    elif mode == "stats":
        compare_token_counts()

    elif mode == "clear":
        clear_non_token_files()

    elif mode == "test-sample":
        sample_test()

    elif mode == "test-freq":
        exponential_test()
    elif mode == "tmp-revision":
        process_in_files()
    else:
        print(f"Unknown mode: {mode}")
        print("Available functionalities: collect, stats, clear, test-sample, test-freq")
