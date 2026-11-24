import openai, os
from degenerate.errors import GenerationError, TransientError, ConfigError, OutputError 

def call_openrouter(model, sys_input, txt_input):
    """
    Wraps a simple prompt of a model delivered via OpenRouter
    Uses the openai SDK
    """
    if not os.environ.get("OPENROUTER_API_KEY"):
        raise ConfigError("OPENROUTER_API_KEY not set")

    options = model.get("options", {}) 
    effort = options.get("effort")
    max_output_tokens = options.get("max_output_tokens", 20000)
    
    # gets API Key from environment variable OPENROUTER_API_KEY
    client = openai.OpenAI(
      base_url="https://openrouter.ai/api/v1",
      api_key=os.getenv("OPENROUTER_API_KEY"),
    )

    kwargs = {
        "model": model["name"],
        "input": txt_input,
        "instructions": sys_input,
        "max_output_tokens": max_output_tokens,
    }

    if effort is not None:
        kwargs["reasoning"] ={"effort": effort}

    try:
        response = client.responses.create(**kwargs )
    except (openai.BadRequestError, openai.AuthenticationError, openai.PermissionDeniedError, openai.NotFoundError) as e:
        # 400, 401, 403, 404
        raise ConfigError(f"OpenAI {type(e).__name__}: {e}") from e
    except (openai.ConflictError, openai.RateLimitError, openai.InternalServerError, openai.APIConnectionError)  as e:
        # 409, 429, 5xx, connection errors
        raise TransientError(f"OpenAI {type(e).__name__}: {e}") from e
    except openai.APIError as e:
        # anything else
        raise GenerationError(f"OpenAI {type(e).__name__}: {e}") from e
                    
    status = response.status
    thought_tokens = response.usage.output_tokens_details.reasoning_tokens
    output_tokens = response.usage.output_tokens

    if status != "completed":
        if response.incomplete_details:
            reason = response.incomplete_details.reason
        elif response.error:
            reason = f"{response.error.code}: {response.error.message}"
        else:
            reason = "unknown"
        raise OutputError(f"OpenRouter response not completed: status {status}, reason {reason}, total output tokens {output_tokens}")
                            
    response = {
        "id": response.id,
        "status": status,
        "output": response.output_text,
        "thought_tokens": thought_tokens,
        "output_tokens": output_tokens-thought_tokens
    }

    return response
