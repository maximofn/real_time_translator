import ollama

response = ollama.chat(model='llama3.2_translator_1B:latest', messages=[
  {
    'role': 'user',
    'content': 'the white table is in the kitchen',
  },
])
print(response['message']['content'])

class Llama_3_1_1B:
    def __init__(self, model='llama3.2_translator_1B:latest'):
        self.model = model
    
    def translate(self, text):
        response = ollama.chat(model='llama3.2_translator_1B:latest', messages=[
            {
                'role': 'user',
                'content': text,
            },
        ])
        return response['message']['content']


