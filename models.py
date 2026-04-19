from pydantic import BaseModel
from typing import List
from enum import Enum

class GenerationMode(str, Enum):
    COPYWRITING = "Copywriting"
    SOCIAL = "Social"
    BLOG = "Blog"
    TECHNICAL = "Technical"


class Context(BaseModel):
    """Incoming context — plain text."""
    context: str

class GrammarCheck(BaseModel):
    """Check grammar of the context"""
    correct_text: str

class AlternativeOfContext(BaseModel):
    """generate an alternative of the context"""
    alternative_text: str

class Translate(BaseModel):
    """Translate the given context"""
    translated_text: str

class GenerateNextLine(BaseModel):
    """Generate next line according to the context"""
    next_line: str
