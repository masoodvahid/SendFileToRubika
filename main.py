from rubpy import Client
from tqdm import tqdm
import requests
import os

# Replace with your actual authentication token
auth_token = 'Auth Token'

# Replace with your actual channel ID
channel_id = 'CHANNEL ID'

# The message you want to send
content = '`hello` __from__ **rubpy**'

def download_video_with_progress(url, output_path):
    try:
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024  # 1 Kilobyte
        t = tqdm(total=total_size, unit='iB', unit_scale=True, desc="Downloading")

        with open(output_path, 'wb') as file:
            for data in response.iter_content(block_size):
                t.update(len(data))
                file.write(data)
        t.close()

        if total_size != 0 and t.n != total_size:
            print("ERROR, something went wrong")
    except Exception as e:
        print(f"Error downloading video: {e}")

def upload_video_with_progress(client, channel_id, video_path):
    file_size = os.path.getsize(video_path)
    t = tqdm(total=file_size, unit='iB', unit_scale=True, desc="Uploading")

    with open(video_path, 'rb') as f:
        while True:
            chunk = f.read(1024)
            if not chunk:
                break
            # Simulate upload by updating the progress bar
            t.update(len(chunk))
            # Here you would normally send the chunk to the server
            # For example, using requests.post or similar
            # requests.post(upload_url, data=chunk)
            # Since we don't have the actual upload URL or method, this is a placeholder
    t.close()

def send_video_with_progress(client, channel_id, video_url):
    temp_video_path = 'temp_video.mp4'
    download_video_with_progress(video_url, temp_video_path)
    upload_video_with_progress(client, channel_id, temp_video_path)
    os.remove(temp_video_path)

def main():
    video_url = input("Please enter the video URL: ")

    with Client("Rubika", auth=auth_token, display_welcome=False) as rubika:
        send_video_with_progress(rubika, channel_id, video_url)

if __name__ == '__main__':
    main()