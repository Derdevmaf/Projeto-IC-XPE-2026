from google import genai

client = genai.Client(api_key="AIzaSyCSDgXx25RVeDvxhSU0Vwk7RGujGhIT6gc")

models = client.models.list()

for model in models:
    print(model.name)

