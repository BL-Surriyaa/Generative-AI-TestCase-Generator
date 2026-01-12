from google import genai
from google.genai.types import GenerateContentConfig
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Create Gemini client
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# Utility function to read files
def read_file(path):
    with open(path, "r", encoding="utf-8") as file:
        return file.read()

# Load system prompt and BDD
system_prompt = read_file("Prompts/generate_testcases_prompt.txt")
bdd_content = read_file("BDDRequirement/EJET_PracticeApp_BDD_AS_IS.txt")

# 🔑 Combine system instruction + BDD into ONE input
final_prompt = f"""
SYSTEM INSTRUCTION:
{system_prompt}

--------------------------------------------

BDD DOCUMENT:
{bdd_content}
"""

# Generate test cases
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=final_prompt,
    config=GenerateContentConfig(
        temperature=0.2
    )
)

# Extract output
testcases_output = response.text

# Save output
os.makedirs("Output", exist_ok=True)
with open("Output/testcases.txt", "w", encoding="utf-8") as f:
    f.write(testcases_output)

print("✅ Test cases generated successfully.")
