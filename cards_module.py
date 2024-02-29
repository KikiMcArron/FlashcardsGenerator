from openai import OpenAI


class OpenAIComms:
    """Class responsible for handling communication with the OpenAI via API."""

    def __init__(self, api_key):
        self.api_key = api_key
        self.client = OpenAI(api_key=self.api_key)

    def generate_flashcards(self, model, content):
        """Generate flashcards based on the prompt."""
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {'role': 'system', 'content': 'You are a helpful assistant.'},
                    {'role': 'user', 'content': f'Generate flashcards for the given text, based on content and '
                                                f'information from text. Return the flashcards in the JSON format. '
                                                f'The text is:\n\n{content}'
                     }
                ],
                max_tokens=1000,
                temperature=0.5,
                top_p=1.0,
                frequency_penalty=0.0)
            return response.choices[0].message.content
        except Exception as e:
            print(f'Error occurred while generating flashcards: {e}')
            return None
