from google import genai
from google.genai import _interactions_errors as gerr
from degenerate.errors import GenerationError, TransientError, ConfigError, OutputError 

def call_gemini(model, sys_input, txt_input, max_output_tokens=12000):
    """
    Wraps a simple prompt of a Gemini model
    """
    options = model.get("options", {}) 
    thinking_level = options.get("thinking_level", "medium")

    client = genai.Client()

    try:
        interaction = client.interactions.create(
            model=model["name"],
            system_instruction = sys_input,
            input=txt_input,
            generation_config={
                "thinking_level": thinking_level,
                "thinking_summaries": None,
                "max_output_tokens": max_output_tokens,
            },
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
        # to do: log failure interactions
        # interaction.to_dict()
        #print(interaction.to_json())
        raise OutputError(f"Gemini status {status}, thought tokens {thought_tokens}, total tokens {output_tokens}")
        
    response = {
        "id": interaction.id,
        "status": status,
        "output": interaction.output_text,
        "thought_tokens": thought_tokens,
        "output_tokens": output_tokens
    }

    return response

