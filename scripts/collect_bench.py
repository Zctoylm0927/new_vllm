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
    else:
        print(f"Unknown mode: {mode}")
        print("Available functionalities: collect, stats, clear, test-sample")
