from helper import get_settings
from models import SystemPrompt
from controllers.model_router import get_working_chat
settings = get_settings()
prompt = SystemPrompt(style="concise", role="geography expert").get_prompt()
formatted_prompt = prompt.format(user_input="عايزك تشرحلى ايه الاساس العلمى ورا RNN باختصار وبدون تعقيد")

response = get_working_chat(settings, formatted_prompt)
print(response.content)