import os
from google import genai
from google.genai import _interactions_errors as gerr
from degenerate.errors import GenerationError, TransientError, ConfigError, OutputError 
from degenerate.paths import FAILED_DIR

def call_gemini(model, sys_input, txt_input, call_id=None):
    """
    Wraps a simple prompt of a Gemini model
    """    
    if not os.environ.get("GEMINI_API_KEY"):
        raise ConfigError("GEMINI_API_KEY not set")

    options = model.get("options", {}) 
    thinking_level = options.get("effort")
    max_output_tokens = options.get("max_output_tokens", 20000)

    client = genai.Client()

    config = {
                "thinking_summaries": None,
                "max_output_tokens": max_output_tokens,
    }
    
    if thinking_level is not None:
        config["thinking_level"] = thinking_level

    try:
        interaction = client.interactions.create(
            model=model["name"],
            system_instruction = sys_input,
            input=txt_input,
            generation_config=config,
            stream=False
        )
    except (gerr.BadRequestError, gerr.AuthenticationError, gerr.NotFoundError, gerr.PermissionDeniedError) as e:
        # 400, 401, 403, 404
        raise ConfigError(f"Gemini {type(e).__name__}: {e}") from e
    except (gerr.ConflictError, gerr.RateLimitError, gerr.InternalServerError, gerr.APIConnectionError)  as e:
        # 409, 429, 5xx, connection errors
        raise TransientError(f"Gemini {type(e).__name__}: {e}") from e
    except gerr.APIError as e:
        # anything else
        raise GenerationError(f"Gemini {type(e).__name__}: {e}") from e

    status = interaction.status
    thought_tokens = interaction.usage.total_thought_tokens
    output_tokens = interaction.usage.total_output_tokens

    if status != "completed":
        FAILED_DIR.mkdir(exist_ok=True)
        (FAILED_DIR / f"{call_id}_response.json").write_text(
            interaction.model_dump_json(indent=2, exclude_none=True),
            encoding="utf-8",
        )
        raise OutputError(f"Gemini status {status}, thought tokens {thought_tokens}, total tokens {output_tokens}")
        
    response = {
        "id": interaction.id,
        "status": status,
        "output": interaction.output_text,
        "thought_tokens": thought_tokens,
        "output_tokens": output_tokens
    }

    return response

