from dotenv import find_dotenv, load_dotenv
from transformers import pipeline
from langchain import PromptTemplate, LLMChain, OpenAI
import requests
import os

load_dotenv(find_dotenv())
HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

#image caption
def img2text(url):
    image_to_text = pipeline("image-to-text", model="Salesforce/blip-image-captioning-base", max_new_tokens=20)

    text = image_to_text(url)[0]["generated_text"]

    print(text)
    return text

#generate story
def generate_story(scenario):
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
    template = """
    You are a story teller.
    You generate stories based off of a simple image caption. The story should be no more than 40 words.
    The story you generate should be in the slightly comedic style of "Fuzzy Memories" from the Saturday Night Live show."

    CONTEXT: {scenario}
    STORY:
    """
    prompt = PromptTemplate(template=template, input_variables=["scenario"])
    story_llm = LLMChain(llm=OpenAI(
        model_name="gpt-3.5-turbo", temperature=1), prompt=prompt, verbose=True)
    
    story = story_llm.predict(scenario=scenario)

    print(story)
    return story


#generate speech
def text2speech(message):
    API_URL = "https://api-inference.huggingface.co/models/espnet/kan-bayashi_ljspeech_vits"
    headers = {"Authorization": f"Bearer {HUGGINGFACEHUB_API_TOKEN}"}
    payloads = {
        "inputs": message,
    }

    response = requests.post(API_URL, headers=headers, json=payloads)
    with open('audio.flac', 'wb') as file:
        file.write(response.content)


scenario = img2text("photo.png")
story = generate_story(scenario)
text2speech(story)
