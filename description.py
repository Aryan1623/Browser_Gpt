from transformers import pipeline
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load a text-generation model for explanation
generator = pipeline("text-generation", model="gpt2")

@app.post("/describe")
async def describe_idea(request: Request):
    body = await request.json()
    topic = body.get("topic")

    if not topic:
        return {"error": "No topic provided."}

    try:
        prompt = (
            f"Explain the topic '{topic}' in simple terms for beginners. "
            "Include what it is, how it works, and why it's important."
        )

        # Generate text
        result = generator(prompt, max_length=len(prompt.split()) + 100, num_return_sequences=1)[0]['generated_text']

        # Safely remove prompt from the beginning
        if result.startswith(prompt):
            description = result[len(prompt):].strip()
        else:
            # fallback: attempt to extract the description heuristically
            description = result.split(":", 1)[-1].strip()

        return {"description": description}
    
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)