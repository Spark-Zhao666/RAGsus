import requests
import time
import os
from dotenv import load_dotenv
load_dotenv()

suno_api_key = os.getenv("SUNO_API")

def generate_music(prompt,suno_api_key=suno_api_key):
    url = "https://dzwlai.com/apiuser/_open/suno/music/generate"

    payload = {
        "expectAiModel": "suno",
        "inputType": "10",
        "mvVersion": "chirp-v4",
        "makeInstrumental": True,
        "gptDescriptionPrompt": prompt,
        "callbackUrl": ""
    }
    headers = {
        "x-token": suno_api_key,
        "x-userId": "1000",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "User-Agent": "PostmanRuntime-ApipostRuntime/1.1.0",
        "Connection": "keep-alive",
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    try:
        response_data = response.json()
        task_id = response_data["data"]["taskBatchId"]
        if not task_id:
            raise ValueError("Can't get task ID")
    except Exception as e:
        raise RuntimeError("Unexpected response format")

    result_url = f"https://dzwlai.com/apiuser/_open/suno/music/getState?taskBatchId={task_id}"
    # max_retries = 10
    retry_interval = 10  # 秒

    print("Pending...")
    while True:
        time.sleep(retry_interval)
        result_response = requests.request("GET", result_url, json=payload, headers=headers)
        result_data = result_response.json()["data"]
        
        if result_data['taskStatus'] == "finished":
            audio_url = result_data["items"][0]['cld2AudioUrl']
            print("Finished!")
            return audio_url
if __name__ == '__main__':
    print(generate_music("A gentle, melancholic piano ballad with soft vocals, expressing the bittersweet pain of loss but also the beautiful memories that remain, to help process grief and bring a sense of quiet comfort."))