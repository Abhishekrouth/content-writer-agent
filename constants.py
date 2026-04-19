import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True)

class ENV_VAR:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class Constants:
    MODEL_NAME = "gemini-2.5-flash"
    MAX_LENGTH = 256

class GENERATION:
    TEMPERATURE_GRAMMAR = 0.0
    TEMPERATURE_ALTERNATIVE = 0.7
    TEMPERATURE_TRANSLATE = 0.0
    TEMPERATURE_NEXT_LINE = 0.9

class MESSAGE:
    error_grammar = "Error in Grammar Check"
    error_alternative = "Error in Generating Alternative"
    error_translate =  "Error in Translting"
    error_next_line = "Error in Generating Next Line"

    success_grammar = "Grammar Checked Successfully"
    success_alternative = "Alternative Generated Successfully"
    success_translate = "Translated Successfully"
    success_next_line = "Next Line Generated Successfully"