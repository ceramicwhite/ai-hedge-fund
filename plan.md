# AI Hedge Fund Project - Environment Variable & Docker Configuration Plan

## Current Issues

### 1. Environment Variable Support
- The project needs to support two additional environment variables:
  - `OPENAI_BASE_URL`: For specifying a custom OpenAI API endpoint
  - `OPENAI_MODEL`: For overriding the selected model

### 2. Docker Dependency Issue
- Error message: `ModuleNotFoundError: No module named 'dotenv'`
- Despite `python-dotenv` being correctly defined in pyproject.toml, it's not available in the Docker container

## Implementation Status

### Completed Changes
- ✅ Updated `.env.example` to include documentation for both new environment variables
- ✅ Modified `src/llm/models.py` to support custom base URL and model override:
  ```python
  # Check for custom base URL
  base_url = os.getenv("OPENAI_BASE_URL")
  
  # Check for model override
  model_override = os.getenv("OPENAI_MODEL")
  if model_override:
      print(f"Using model override: {model_override} instead of {model_name}")
      model_name = model_override
      
  # Create the ChatOpenAI instance with the appropriate parameters
  kwargs = {
      "model": model_name,
      "api_key": api_key
  }
  
  if base_url:
      kwargs["base_url"] = base_url
      
  return ChatOpenAI(**kwargs)
  ```

### Pending Changes
- 🔄 Update `compose.yml` to build from the local Dockerfile instead of using a pre-built image
  - Current configuration uses a pre-built image (`ceramicwhite/ai-hedge-fund:arm64`) but mounts local code
  - This creates a mismatch between installed dependencies in the image and required dependencies in the code

## Recommended Solution

For the Docker issue, modify `compose.yml` to use the local Dockerfile instead of the pre-built image:

```yaml
services:
  ai-hedge-fund:
    container_name: ai-hedge-fund
    build:
      context: .
      dockerfile: Dockerfile
    # Remove the image: line
    volumes:
      - ./:/ai-hedge-fund
    env_file:
      - .env
    stdin_open: true
    tty: true
    command: poetry run python src/main.py --ticker PLTR
```

This change will ensure that all dependencies from pyproject.toml (including python-dotenv) are properly installed during the container build process.

## Implementation Steps

1. Switch to Code mode to edit the `compose.yml` file
2. Update the file to build from the local Dockerfile
3. Test the application to ensure it works correctly

## Future Considerations

- The Docker image `ceramicwhite/ai-hedge-fund:arm64` might need to be updated to include the proper dependencies
- Alternatively, consider creating a requirements.txt file alongside poetry for Docker build processes that might use pip instead of poetry