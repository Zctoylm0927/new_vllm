import numpy as np
from online import get_length_request
# 模拟每秒钟的请求数量以及每个请求的长度
def generate_requests_and_lengths(lambda_req, lambda_length, time_window):
    requests_per_second = np.random.poisson(lambda_req, time_window)
    lengths_per_request = []
    
    print(requests_per_second)
    for requests in requests_per_second:
        # 对每个请求生成一个句子长度，长度服从泊松分布
        lengths_per_request.append(np.random.poisson(lambda_length, requests))
    
    return requests_per_second, lengths_per_request

# 设置参数
lambda_req = 3    # 每秒请求数的平均值
lambda_length = 20  # 请求句子长度的平均值
time_window = 6

# 生成每秒请求数量和句子长度
requests_per_second, lengths_per_request = generate_requests_and_lengths(lambda_req, lambda_length, time_window)

total_requests = []
# # 输出每秒的请求数量以及每个请求的句子长度
with open("request.txt", "w") as file:
    for second in range(time_window):
        print(f"Second {second}:")
        print(f"  Number of requests: {requests_per_second[second]}")
        print(f"  Sentence lengths: {lengths_per_request[second]}")