from google import genai
from dotenv import load_dotenv
import os

# Load env variables
load_dotenv()

# Create client
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# Simple test
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Say OK"
)

print(response.text)
