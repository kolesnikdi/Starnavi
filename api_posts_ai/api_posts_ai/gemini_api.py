import google.generativeai as gemini
from google.generativeai.types import HarmCategory, HarmBlockThreshold

import os


class GenerativeClient:
    _name = "gemini-1.5-flash"
    _model = None

    @property
    def model(self):
        # Lazy model creation
        if self._model is None:
            gemini.configure(api_key=os.environ.get('GEMINI_API_KEY'))
            self._model = gemini.GenerativeModel(model_name=self._name)
        return self._model

    def is_swearing(self, text: str):
        # Checks posts for swear words
        message = (f"Answer me only with a number. \n"
                   f"If the text ({text}) does not contain any swear words, your answer must be 0 else 1")
        response = self.model.generate_content(
            message,
            generation_config=gemini.types.GenerationConfig(
                candidate_count=1,
                temperature=1.0,
            ),
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }

        )
        try:
            bool_response = bool(int(response.text))
            return bool_response
        except Exception:
            return True

    def reply(self, text: list, creativity: float):
        # Makes reply to comments
        response = self.model.generate_content(
            text,
            generation_config=gemini.types.GenerationConfig(
                candidate_count=1,
                temperature=creativity,
            ),
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            }

        )
        try:
            response = response.text
            return response
        except Exception:
            return False


ai = GenerativeClient()
