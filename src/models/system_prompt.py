from langchain_core.prompts import PromptTemplate

class SystemPrompt:
    def __init__(self, style: str, role: str):
        self.style = style
        self.role = role

    def get_prompt(self) -> PromptTemplate:
        return PromptTemplate(
            input_variables=["user_input"],
            template=f"""You are a {self.role} helping the user answer his question in a style: {self.style}.
            The output should be a JSON object with the answer and the reasoning behind it.
            answer at the same language as the question and if the question is in Arabic, answer in Arabic.
            if the question is in English, answer in English.
            if the question have any other language, answer in English.
            if the question is not clear, ask for clarification.
            if the question have arabic and english words, answer in the language that is more dominant in the question.
            User's question: {{user_input}}"""
        )