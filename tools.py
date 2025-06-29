import os
from dotenv import load_dotenv
load_dotenv()

from typing import ClassVar
from crewai.tools import BaseTool
from crewai_tools.tools import SerperDevTool
from langchain_community.document_loaders import PyPDFLoader


# * Creating search tool (already a proper tool)
search_tool = SerperDevTool()


# * Tool 1: Blood Test Report Tool
class BloodTestReportTool(BaseTool):
    name: ClassVar[str] = "read_blood_report"
    description: str = "Reads a PDF blood test report and returns the cleaned text."

    def _run(self, path: str = "data/sample.pdf") -> str:
        docs = PyPDFLoader(file_path=path).load()
        return "\n".join([doc.page_content.replace("\n\n", "\n") for doc in docs])

    def _arun(self, path: str = "data/sample.pdf") -> str:
        raise NotImplementedError("Async not supported for this tool")


# * Tool 2: Nutrition Analysis Tool
class NutritionTool(BaseTool):
    name: ClassVar[str] = "analyze_nutrition"
    description: str = "Analyzes the provided blood report data to give nutritional insights."

    def _run(self, blood_report_data: str) -> str:
        processed_data = blood_report_data
        while "  " in processed_data:
            processed_data = processed_data.replace("  ", " ")
        
        # TODO: Replace with real nutrition logic
        return "Nutrition analysis functionality to be implemented"

    def _arun(self, blood_report_data: str) -> str:
        raise NotImplementedError("Async not supported for this tool")


# * Tool 3: Exercise Planning Tool
class ExerciseTool(BaseTool):
    name: ClassVar[str] = "create_exercise_plan"
    description: str = "Creates a personalized exercise plan based on the blood report."

    def _run(self, blood_report_data: str) -> str:
        # TODO: Replace with real exercise planning logic
        return "Exercise planning functionality to be implemented"

    def _arun(self, blood_report_data: str) -> str:
        raise NotImplementedError("Async not supported for this tool")
