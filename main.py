import requests
import io
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, UploadFile
import os
load_dotenv()
# Initialize FastAPI app
app = FastAPI(
    root_path="/",  # Ensure correct root path
    servers=[{"url": "https://iitm-project-2.onrender.com", "description": "Render Server"}]
)


# OpenAI Proxy API details
OPENAI_PROXY_TOKEN =os.getenv("OPENAI_PROXY_TOKEN")
OPENAI_PROXY_URL = "http://aiproxy.sanand.workers.dev/openai/v1/chat/completions"  # Replace with your correct OpenAI proxy URL

# Function to send question and file content to OpenAI
def get_openai_response(question, file_name=None, file_content=None):
    try:
        headers = {
            "Authorization": f"Bearer {OPENAI_PROXY_TOKEN}",
            "Content-Type": "application/json",
        }

        # Construct system and user messages
        messages = [{"role": "system", "content": "You are an AI that processes files and answers user queries."}]
        messages.append({"role": "user", "content": question})

        # If a file is provided, send its content to OpenAI
        if file_content:
            try:
                decoded_content = file_content.decode(errors="ignore")  # Decode text-based files
            except UnicodeDecodeError:
                decoded_content = "[Binary file content omitted]"

            messages.append({
                "role": "user",
                "content": f"Here is the uploaded file '{file_name}'.\n\n{decoded_content}"
            })

        # API Payload
        payload = {
            "model": "gpt-4o-mini",  # Corrected model name
            "messages": messages,
        }

        # Send request to OpenAI API
        response = requests.post(OPENAI_PROXY_URL, json=payload, headers=headers, timeout=10)
        response_json = response.json()

        # Ensure 'choices' exists in response
        if "choices" not in response_json:
            return f"Unexpected API response: {response_json}"

        return response_json["choices"][0]["message"]["content"].strip()

    except requests.exceptions.Timeout:
        return "Error: OpenAI API request timed out."
    except requests.exceptions.RequestException as e:
        return f"Error: Failed to connect to OpenAI Proxy API: {str(e)}"
    except Exception as e:
        return f"Error querying OpenAI API: {str(e)}"

@app.post("/api/")
async def process_request(
    question: str = Form(...), 
    file: UploadFile = File(None)
):
    try:
        file_content = None
        file_name = None

        if file:
            file_content = await file.read()
            file_name = file.filename

        # Get OpenAI response
        answer = get_openai_response(question, file_name, file_content)

        return {"answer": answer}

    except Exception as e:
        return {"answer": f"Error processing request: {str(e)}"}
