import requests
import time
import os

# 配置API参数
API_KEY = os.getenv("SUNO_API")  # 从AceData或302ai平台获取[1,3](@ref)
API_ENDPOINT = "https://api.acedata.cloud/suno/audios"  # 或使用302ai的接口[1](@ref)

def generate_song(prompt, lyrics, style="流行"):
    """生成歌曲"""
    headers = {
        "authorization": f"Bearer {API_KEY}",
        "content-type": "application/json"
    }
    
    payload = {
        "action": "generate",
        "prompt": prompt,
        "model": "chirp-v3-5",  # 推荐使用最新模型[1](@ref)
        "lyric": lyrics,
        "custom": True,
        "style": style,
        "instrumental": False
    }

    response = requests.post(API_ENDPOINT, json=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            return data['data']  # 返回生成的音频信息[1,3](@ref)
        else:
            raise Exception(f"生成失败: {data.get('message')}")
    else:
        raise Exception(f"API请求失败: {response.status_code}")

def download_audio(audio_info, save_path="songs"):
    """下载音频文件"""
    os.makedirs(save_path, exist_ok=True)
    
    for track in audio_info:
        mp3_url = track.get('audio_url')
        title = track.get('title', 'untitled').replace(' ', '_')
        
        try:
            response = requests.get(mp3_url)
            filename = f"{save_path}/{title}.mp3"
            
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"下载完成: {filename}")
        except Exception as e:
            print(f"下载失败: {str(e)}")

# 使用示例
if __name__ == "__main__":
    lyrics = """[Verse]
让我给您拜个年，祝你生活蜜蜜甜
来年有钱又有闲，新年愿望都实现
[Chorus]
点鞭炮，福星照，财源广进无烦扰
愿君一年好运道，全家团圆真热闹！"""
    
    try:
        # 生成歌曲
        result = generate_song(
            prompt="一首春节的拜年歌曲",
            lyrics=lyrics,
            style="传统民谣"
        )
        
        # 下载音频
        download_audio(result)
        
    except Exception as e:
        print(f"执行出错: {str(e)}")