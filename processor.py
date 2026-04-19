import json
from google import genai
from google.genai import types
from constants import ENV_VAR, Constants, GENERATION
from prompts import (
    GRAMMAR_CHECK_PROMPT,
    GENERATE_ALTERNATIVE_PROMPT,
    TRANSLATE_PROMPT,
    GENERATE_NEXT_LINE_PROMPT
)
from models import (
    GrammarCheck,
    AlternativeOfContext,
    Translate,
    GenerateNextLine
)

class Processor:
    def __init__(self):
        self.client = genai.Client(api_key=ENV_VAR.GEMINI_API_KEY)
        self.model_name = Constants.MODEL_NAME

    def process(self, text, action, context="", language="English", mode="Copywriting"):
        try:
            if action == "Grammar":
                prompt = GRAMMAR_CHECK_PROMPT.format(context=context or text)
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=GENERATION.TEMPERATURE_GRAMMAR,
                        response_mime_type="application/json",
                        response_schema=GrammarCheck
                    )
                )
                if getattr(response, "parsed", None):
                    return response.parsed.correct_text
                else:
                    return ""

            elif action == "Alternative":
                prompt = GENERATE_ALTERNATIVE_PROMPT.format(context=context or text)
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=GENERATION.TEMPERATURE_ALTERNATIVE,
                        response_mime_type="application/json",
                        response_schema=AlternativeOfContext
                    )
                )
                if getattr(response, "parsed", None):
                    return response.parsed.alternative_text
                else:
                    return ""

            elif action == "Translate":
                prompt = TRANSLATE_PROMPT.format(context=context or text, language=language)
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=GENERATION.TEMPERATURE_TRANSLATE,
                        response_mime_type="application/json",
                        response_schema=Translate
                    )
                )
                if getattr(response, "parsed", None):
                    return response.parsed.translated_text
                else:
                    return ""

            elif action == "GenerateText":
                prompt = GENERATE_NEXT_LINE_PROMPT.format(context=context or text, mode=mode)
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=GENERATION.TEMPERATURE_NEXT_LINE,
                        response_mime_type="application/json",
                        response_schema=GenerateNextLine
                    )
                )
                if getattr(response, "parsed", None):
                    return response.parsed.next_line
                else:
                    return ""
            
            return ""
            
        except Exception as e:
            print(f"Error processing {action}: {e}")
            raise e
