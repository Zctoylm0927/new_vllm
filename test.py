import time
from test_tpot import get_tpot
from test_ttft import get_ttft
import json

with open('request.json', 'r') as file:
    data = json.load(file)
    
def send_questions_per_second(data):
    for t, question_info in data.items():
        if question_info:
            for question in question_info:
                question = question["sentence"]
                print(f"sending question: {question}")
                
                ttft = get_ttft(question)
                tpot = get_tpot(question)
                print(f"ttft: {ttft:.3f} , tpot: {tpot} tokens/s")

        time.sleep(1)
        
if __name__ == "__main__":
    send_questions_per_second(data)