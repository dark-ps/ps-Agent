import sys
import requests

# Usage (via TOOL: run_file, or directly): 
# python upload-files.py <file-path> 
# "python" – "python3 -->> APPLIES TO THE SYSTEM 
# Uploads the file anonymously to catbox.moe and prints back the public URL.


def загрузить(file_path):
	try:
		with open(file_path, 'rb') as fh:
			data = {'reqtype': 'fileupload', 'userhash': ''}
			files = {'fileToUpload': fh}
			resp = requests.post("https://catbox.moe/user/api.php", data=data, files=files, timeout=120)
		if resp.status_code == 200 and resp.text.startswith('https://'):
			print(resp.text.strip())
		else:
			print(f"unexpected – ({resp.status_code}) {resp.text.strip()}")
	except FileNotFoundError:
		print(f"NOT FOUND: {file_path}")
	except Exception as e:
		print(f"{e}")


if __name__ == '__main__':
	if len(sys.argv) < 2:
		print("Usage: python upload-files.py <file-path>")
		sys.exit(1)
	загрузить(sys.argv[1])