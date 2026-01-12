from google import genai
from google.genai.types import GenerateContentConfig
from dotenv import load_dotenv
from openpyxl import Workbook
import os
import json
import re
import logging

# -------------------------------------------------------
# 1. LOGGING CONFIGURATION (FILE + CONSOLE)
# -------------------------------------------------------
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "genai_testcase_generation.log")

logger = logging.getLogger("GenAITestCaseGenerator")
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

# Avoid duplicate handlers if script reruns
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
OUTPUT_FILE = "EJET_TestCases.xlsx"

# -------------------------------------------------------
# 6. LOAD PROMPT AND BDD
# -------------------------------------------------------
system_prompt = read_file(SYSTEM_PROMPT_PATH)
bdd_content = read_file(BDD_PATH)
logger.info("System prompt and BDD loaded")

# -------------------------------------------------------
# 7. FINAL PROMPT
# -------------------------------------------------------
final_prompt = f"""
SYSTEM INSTRUCTION:
{system_prompt}

--------------------------------------------------

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
        temperature=0.1
    )
)

raw_output = response.text.strip()
logger.info("Gemini response received")

# -------------------------------------------------------
# 9. EXTRACT JSON
# -------------------------------------------------------
logger.info("Extracting JSON from Gemini output")

json_match = re.search(r"\{[\s\S]*}", raw_output)

if not json_match:
    logger.error("No JSON object found in Gemini response")
    raise Exception("❌ No JSON object found in Gemini response")

json_text = json_match.group(0)

try:
    testcases_json = json.loads(json_text)
    logger.info("JSON parsed successfully")
except json.JSONDecodeError as e:
    logger.error(f"Invalid JSON returned by Gemini: {e}")
    raise Exception(f"❌ Invalid JSON returned by Gemini: {e}")

# -------------------------------------------------------
# 10. CREATE EXCEL
# -------------------------------------------------------
logger.info("Creating Excel workbook")

wb = Workbook()
ws = wb.active
ws.title = "TestCases"

headers = [
    "Test Case ID",
    "Epic",
    "Feature",
    "Scenario Name",
    "Description",
    "Objective",
    "Test Data",
    "Test Steps",
    "Expected Result",
    "Practice Type",
    "Priority",
    "Severity",
    "Automation Tags"
]

ws.append(headers)

# -------------------------------------------------------
# 11. POPULATE EXCEL
# -------------------------------------------------------
logger.info("Populating Excel rows")

for tc in testcases_json.get("test_cases", []):
    ws.append([
        tc.get("test_case_id", ""),
        tc.get("epic", ""),
        tc.get("feature", ""),
        tc.get("scenario_name", ""),
        tc.get("description", ""),
        tc.get("objective", ""),
        json.dumps(tc.get("test_data", {}), indent=2),
        "\n".join(tc.get("test_steps", [])),
        tc.get("expected_result", ""),
        tc.get("practice_type", ""),
        tc.get("priority", ""),
        tc.get("severity", ""),
        ", ".join(tc.get("automation_tags", []))
    ])

logger.info("All test cases written to Excel")

# -------------------------------------------------------
# 12. SAVE EXCEL
# -------------------------------------------------------
os.makedirs(OUTPUT_DIR, exist_ok=True)
output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
wb.save(output_path)

logger.info(f"Excel file generated successfully: {output_path}")
