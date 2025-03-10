import os
from langchain_anthropic import ChatAnthropic
from langchain_deepseek import ChatDeepSeek
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from enum import Enum
from pydantic import BaseModel
from typing import Tuple, List

def are_openrouter_env_vars_set():
    """Check if OpenRouter environment variables are set."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    model = os.getenv("OPENROUTER_MODEL")
    print(f"DEBUG: Checking OpenRouter env vars - API Key: {'FOUND' if api_key else 'NOT FOUND'}, Model: {'FOUND' if model else 'NOT FOUND'}")
    return bool(api_key) and bool(model)


class ModelProvider(str, Enum):
    """Enum for supported LLM providers"""
    ANTHROPIC = "Anthropic"
    DEEPSEEK = "DeepSeek"
    GEMINI = "Gemini"
    GROQ = "Groq"
    OPENAI = "OpenAI"
    OPENROUTER = "OpenRouter"



class LLMModel(BaseModel):
    """Represents an LLM model configuration"""
    display_name: str
    model_name: str
    provider: ModelProvider

    def to_choice_tuple(self) -> Tuple[str, str, str]:
        """Convert to format needed for questionary choices"""
        return (self.display_name, self.model_name, self.provider.value)
    
    def has_json_mode(self) -> bool:
        """Check if the model supports JSON mode"""
        return not self.is_deepseek() and not self.is_gemini()
    
    def is_deepseek(self) -> bool:
        """Check if the model is a DeepSeek model"""
        return self.model_name.startswith("deepseek")
    
    def is_gemini(self) -> bool:
        """Check if the model is a Gemini model"""
        return self.model_name.startswith("gemini")


# Define base available models
BASE_MODELS = [
    LLMModel(
        display_name="[anthropic] claude-3.5-haiku",
        model_name="claude-3-5-haiku-latest",
        provider=ModelProvider.ANTHROPIC
    ),
    LLMModel(
        display_name="[anthropic] claude-3.5-sonnet",
        model_name="claude-3-5-sonnet-latest",
        provider=ModelProvider.ANTHROPIC
    ),
    LLMModel(
        display_name="[anthropic] claude-3.7-sonnet",
        model_name="claude-3-7-sonnet-latest",
        provider=ModelProvider.ANTHROPIC
    ),
    LLMModel(
        display_name="[deepseek] deepseek-r1",
        model_name="deepseek-reasoner",
        provider=ModelProvider.DEEPSEEK
    ),
    LLMModel(
        display_name="[deepseek] deepseek-v3",
        model_name="deepseek-chat",
        provider=ModelProvider.DEEPSEEK
    ),
    LLMModel(
        display_name="[gemini] gemini-2.0-flash",
        model_name="gemini-2.0-flash",
        provider=ModelProvider.GEMINI
    ),
    LLMModel(
        display_name="[gemini] gemini-2.0-pro",
        model_name="gemini-2.0-pro-exp-02-05",
        provider=ModelProvider.GEMINI
    ),
    LLMModel(
        display_name="[groq] llama-3.3 70b",
        model_name="llama-3.3-70b-versatile",
        provider=ModelProvider.GROQ
    ),
    LLMModel(
        display_name="[openai] gpt-4.5",
        model_name="gpt-4.5-preview",
        provider=ModelProvider.OPENAI
    ),
    LLMModel(
        display_name="[openai] gpt-4o",
        model_name="gpt-4o",
        provider=ModelProvider.OPENAI
    ),
    LLMModel(
        display_name="[openai] o1",
        model_name="o1",
        provider=ModelProvider.OPENAI
    ),
    LLMModel(
        display_name="[openai] o3-mini",
        model_name="o3-mini",
        provider=ModelProvider.OPENAI
    ),
]

# Function to get available models dynamically (including OpenRouter if configured)
def get_available_models() -> List[LLMModel]:
    """Get all available models, including dynamic ones from environment variables."""
    print("\n=== Starting get_available_models() ===")
    all_models = BASE_MODELS.copy()
    print(f"Base models loaded: {len(BASE_MODELS)} models")
    
    # Add OpenRouter models if environment variables are set
    print("Checking for OpenRouter environment variables...")
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY", "")
    openrouter_model = os.getenv("OPENROUTER_MODEL", "")
    print(f"OPENROUTER_API_KEY: {'Set (length: ' + str(len(openrouter_api_key)) + ')' if openrouter_api_key else 'NOT SET'}")
    print(f"OPENROUTER_MODEL: {openrouter_model if openrouter_model else 'NOT SET'}")
    
    if openrouter_api_key and openrouter_model:
        print(f"OpenRouter environment variables found. Adding model: {openrouter_model}")
        # Extract a display name from the model
        display_name = openrouter_model
        if "/" in openrouter_model:
            # For models like "google/gemini-2.0-flash-001", extract "gemini-2.0-flash-001"
            display_name = openrouter_model.split("/")[-1]
        
        openrouter_model_obj = LLMModel(
            display_name=f"[openrouter] {display_name}",
            model_name=openrouter_model,
            provider=ModelProvider.OPENROUTER
        )
        all_models.append(openrouter_model_obj)
        print(f"Added OpenRouter model: {openrouter_model} to available models")
        print(f"Total models now: {len(all_models)}")
    else:
        print("OpenRouter environment variables not properly set. Skipping...")
    
    print("=== Finished get_available_models() ===\n")
    return all_models

# Get models on demand rather than at module load time
def get_llm_order():
    """Get LLM order in the format expected by the UI."""
    return [model.to_choice_tuple() for model in get_available_models()]

# For backward compatibility (some code might access AVAILABLE_MODELS directly)
AVAILABLE_MODELS = BASE_MODELS

# LLM_ORDER will be generated dynamically when needed
LLM_ORDER = get_llm_order()

def get_model_info(model_name: str) -> LLMModel | None:
    """Get model information by model_name"""
    return next((model for model in AVAILABLE_MODELS if model.model_name == model_name), None)

def get_model(model_name: str, model_provider: ModelProvider) -> ChatOpenAI | ChatGroq | None:
    # Handle OpenRouter
    if model_provider == ModelProvider.OPENROUTER:
        # Get and validate API key
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            print(f"API Key Error: Please make sure OPENROUTER_API_KEY is set in your .env file.")
            raise ValueError("OpenRouter API key not found. Please make sure OPENROUTER_API_KEY is set in your .env file.")
            
        print(f"Configuring OpenRouter with model: {model_name}")
        
        # OpenRouter uses the OpenAI client but with specific configuration
        return ChatOpenAI(
            model=model_name,
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            default_headers={
               "HTTP-Referer": "https://github.com/virattt/ai-hedge-fund",
               "X-Title": "AI HEDGE FUND"
           }
        )
    
    # Handle Groq
    elif model_provider == ModelProvider.GROQ:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print(f"API Key Error: Please make sure GROQ_API_KEY is set in your .env file.")
            raise ValueError("Groq API key not found. Please make sure GROQ_API_KEY is set in your .env file.")
        return ChatGroq(model=model_name, api_key=api_key)
    
    # Handle OpenAI
    elif model_provider == ModelProvider.OPENAI:
        # Get and validate API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print(f"API Key Error: Please make sure OPENAI_API_KEY is set in your .env file.")
            raise ValueError("OpenAI API key not found. Please make sure OPENAI_API_KEY is set in your .env file.")
        
        # Check for custom base URL
        base_url = os.getenv("OPENAI_BASE_URL")
        
        # Check for model override
        model_override = os.getenv("OPENAI_MODEL")
        if model_override and model_override != model_name:
            print(f"Using model override from environment variables: {model_override} instead of {model_name}")
            model_name = model_override
        
        # Create standard OpenAI configuration
        kwargs = {
            "model": model_name,
            "api_key": api_key
        }
        
        # Add base_url if specified
        if base_url:
            kwargs["base_url"] = base_url
        
        return ChatOpenAI(**kwargs)
    elif model_provider == ModelProvider.ANTHROPIC:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            print(f"API Key Error: Please make sure ANTHROPIC_API_KEY is set in your .env file.")
            raise ValueError("Anthropic API key not found.  Please make sure ANTHROPIC_API_KEY is set in your .env file.")
        return ChatAnthropic(model=model_name, api_key=api_key)
    elif model_provider == ModelProvider.DEEPSEEK:
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            print(f"API Key Error: Please make sure DEEPSEEK_API_KEY is set in your .env file.")
            raise ValueError("DeepSeek API key not found.  Please make sure DEEPSEEK_API_KEY is set in your .env file.")
        return ChatDeepSeek(model=model_name, api_key=api_key)
    elif model_provider == ModelProvider.GEMINI:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print(f"API Key Error: Please make sure GOOGLE_API_KEY is set in your .env file.")
            raise ValueError("Google API key not found.  Please make sure GOOGLE_API_KEY is set in your .env file.")
        return ChatGoogleGenerativeAI(model=model_name, api_key=api_key)