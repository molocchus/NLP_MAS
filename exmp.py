from swarms.structs.agent import Agent
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from huggingface_hub import login
from swarm_models.huggingface import HuggingfaceLLM

# Hugging Face login
hf_token = "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"
login(token=hf_token)

# TinyLLaMA model
model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

local_llm = HuggingfaceLLM(
    model_id=model_name,
    device="cuda",
    max_length=500
)

# Create swarms agent
agent = Agent(
    agent_name="StudyHelper",
    system_prompt="You are a helpful assistant answering general knowledge questions.",
    max_loops=1,
    autosave=True,
    dashboard=False,
    verbose=True,
    saved_state_path="tiny_llama_agent.json",
    llm=local_llm
)

# English question
question = "What are the benefits of regular exercise?"
out = agent.run(question)
print(out)
