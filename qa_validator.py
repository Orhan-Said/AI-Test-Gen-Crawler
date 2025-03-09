import json
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4",
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0
)

validation_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a QA automation expert reviewing test cases and Page Object Model code."),
    ("user", """Review the following test cases and POM code for correctness, coverage, and adherence to best practices. Provide feedback or suggested improvements.

Test Cases:
{testCases}

POM Code:
{pomCode}

Return your feedback as plain text.""")
])


def validate_test_cases(test_cases, pom_code):
    """
    Validate generated test cases and POM code using an LLM.

    Args:
        test_cases (list): List of test case dictionaries.
        pom_code (str): POM class code.

    Returns:
        str: Validation feedback.
    """
    test_cases_json = json.dumps(test_cases, indent=2)
    prompt_text = validation_prompt.format(
        testCases=test_cases_json, pomCode=pom_code)
    try:
        response = llm.invoke(prompt_text)
        return response.content
    except Exception as e:
        print(f"Error during validation: {e}")
        return "Validation failed due to an error."
