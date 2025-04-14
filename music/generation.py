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

    # 2. 解析响应获取任务ID（假设响应包含ID字段）
    try:
        response_data = response.json()
        task_id = response_data["data"]["taskBatchId"]
        if not task_id:
            raise ValueError("Can't get task ID")
    except Exception as e:
        raise RuntimeError("Unexpected response format")

    # 3. 轮询获取结果（根据API实际情况调整轮询逻辑）
    result_url = f"https://dzwlai.com/apiuser/_open/suno/music/getState?taskBatchId={task_id}"
    # max_retries = 10
    retry_interval = 10  # 秒

    print("Pending...")
    while True:
        time.sleep(retry_interval)
        result_response = requests.request("GET", result_url, json=payload, headers=headers)
        result_data = result_response.json()["data"]
        
        if result_data['taskStatus'] == "finished":
            # 4. 提取音乐URL（根据实际API响应结构调整）
            audio_url = result_data["items"][0]['cld2AudioUrl']  # 或可能是video_url/image_url等
            return audio_url
if __name__ == '__main__':
    print(generate_music("A beautiful day in Paris playing the violin", suno_api_key))