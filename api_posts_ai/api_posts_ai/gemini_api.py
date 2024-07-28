import google.generativeai as gemini_api
from google.generativeai.types import HarmCategory, HarmBlockThreshold

import os


gemini_api.configure(api_key=os.environ.get('GEMINI_API_KEY'))

ai = gemini_api.GenerativeModel(model_name="gemini-1.5-flash")


def perform_ai_task_or_dialogue(message: str or list, creativity: float):

    response = ai.generate_content(message,
                                   generation_config=gemini_api.types.GenerationConfig(
                                       candidate_count=1,
                                       temperature=creativity),
                                   safety_settings={
                                       HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                                       HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                                       HarmCategory.HARM_CATEGORY_UNSPECIFIED: HarmBlockThreshold.BLOCK_NONE,
                                       HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                                       HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                                   }

                                   )
    return response.text
