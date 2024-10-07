from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
# import accelerate
from huggingface_hub import login
from dotenv import load_dotenv
import os

CHECKPOINTS = "Qwen/Qwen2.5-1.5B-Instruct"

class Translator:
    def __init__(self):
        load_dotenv()
        hf_token = os.getenv('HF_TOKEN')
        login(token=hf_token)
        self.model = AutoModelForCausalLM.from_pretrained(
            CHECKPOINTS,
            torch_dtype="auto",
            device_map="auto",
        )
        self.tokenizer = AutoTokenizer.from_pretrained(CHECKPOINTS)
        self.sistem_prompt = {
            "role": "system",
            "content": "You are an expert translator, your mission is to translate texts from English to Spanish. You will receive texts in English, respond only with the Spanish translation, nothing else.",
        }

    def translate(self, prompt):
        messages = [
            self.sistem_prompt,
            {"role": "user", "content": prompt},
        ]
        tokenized_chat = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        model_inputs = self.tokenizer([tokenized_chat], return_tensors="pt").to(self.model.device)
        generated_ids = self.model.generate(
            **model_inputs,
            max_new_tokens=512
        )
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]
        response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        return response
    