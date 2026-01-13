from google import genai
from google.genai.types import GenerateContentConfig
from dotenv import load_dotenv
import os
import logging

# -------------------------------------------------------
# 1. LOGGING CONFIGURATION (FILE + CONSOLE)
# -------------------------------------------------------
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "genai_testcase_generation.log")

logger = logging.getLogger("GenAITestCaseGenerator-TXT")
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# File handler (permanent logs)
file_handler = logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8")
file_handler.setFormatter(formatter)

# Console handler (live logs)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Prevent duplicate logs on re-run
if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

# -------------------------------------------------------
# 2. LOAD ENV VARIABLES
# -------------------------------------------------------
load_dotenv()
logger.info("Environment variables loaded")

# -------------------------------------------------------
# 3. CREATE GEMINI CLIENT
# -------------------------------------------------------
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
logger.info("Gemini client initialized")

# -------------------------------------------------------
# 4. UTILITY: READ FILE
# -------------------------------------------------------
def read_file(path):
    logger.info(f"Reading file: {path}")
    with open(path, "r", encoding="utf-8") as file:
        return file.read()

# -------------------------------------------------------
# 5. PATHS
# -------------------------------------------------------
SYSTEM_PROMPT_PATH = "Prompts/generate_testcases_prompt.txt"
BDD_PATH = "BDDRequirement/EJET_PracticeApp_BDD_AS_IS.txt"
OUTPUT_DIR = "Output"
OUTPUT_FILE = "testcases.txt"

# -------------------------------------------------------
# 6. LOAD PROMPT AND BDD
# -------------------------------------------------------
system_prompt = read_file(SYSTEM_PROMPT_PATH)
bdd_content = read_file(BDD_PATH)
logger.info("System prompt and BDD loaded successfully")

# -------------------------------------------------------
# 7. FINAL PROMPT (SYSTEM + BDD)
# -------------------------------------------------------
final_prompt = f"""
SYSTEM INSTRUCTION:
{system_prompt}

--------------------------------------------

BDD DOCUMENT:
{bdd_content}
"""

# -------------------------------------------------------
# 8. CALL GEMINI
# -------------------------------------------------------
logger.info("Calling Gemini model to generate test cases")

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=final_prompt,
    config=GenerateContentConfig(
        temperature=0.2
    )
)

testcases_output = response.text
logger.info("Gemini response received successfully")

# -------------------------------------------------------
# 9. SAVE OUTPUT TXT
# -------------------------------------------------------
os.makedirs(OUTPUT_DIR, exist_ok=True)
output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)

with open(output_path, "w", encoding="utf-8") as f:
    f.write(testcases_output)

logger.info(f"Test cases written to TXT file: {output_path}")

print("✅ Test cases generated successfully.")
