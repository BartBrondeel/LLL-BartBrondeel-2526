from langchain.chat_models import init_chat_model

GOOGLE_API_KEY = "AIzaSyCUR9TdpKeNuEVBu6t2LM5B_phmPAkS1jo"

model = init_chat_model(
    model="gemini-3-flash-preview",
    model_provider="google-genai",
    api_key=GOOGLE_API_KEY
)

response = model.invoke("is a pen better then a pencil")
response_str = response.content[0]["text"]
print(response_str)
