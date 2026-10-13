import sys
import requests as r

# Usage (via TOOL: run_file, or directly):
# python sandbox.py <language> <code>
# "python" – "python3" -->> APPLIES TO THE SYSTEM
# Sends source code to the Runlet remote sandbox for execution and returns
# the sandbox response. This is NOT a local shell command executor.
#
# Arguments:
# <language> – Sandbox language: python, javascript, cpp, or java.
# <code>     – Complete source code to execute in the remote sandbox.
#
# Example:
# python sandbox.py python 'print("Hello from sandbox!")'
#
# Example with multiline Python:
# python sandbox.py python 'import os; print(os.getcwd())'
#
# Use this tool when you need to execute source code inside the remote
# Runlet sandbox. Pass the programming language and source code as arguments.
# Do NOT execute the supplied code through the local shell or "solo" command.
# The tool itself handles the request to the remote sandbox and returns
# the execution response.

def execute(language,code):
	try:
		response=r.post("https://runlet.codealong.live/execute",json={"language":language,"code":code},timeout=30)
		response.raise_for_status()
		return response.text
	except r.RequestException as error:return f"Request failed: {error}"

if __name__=='__main__':
	if len(sys.argv)<3:
		print("Usage: python sandbox.py <language> <code>")
		sys.exit(1)
	result=execute(sys.argv[1],sys.argv[2])
	print(result)
	if result.startswith("Request failed:"):sys.exit(1)
