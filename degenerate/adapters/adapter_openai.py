import openai, os
from degenerate.errors import GenerationError, TransientError, ConfigError, OutputError 
from degenerate.paths import FAILED_DIR, LOGS_DIR

def call_openai(model, sys_input, txt_input, call_id=None):
    """
    Wraps a simple prompt of an OpenAI model
    """
    if not os.environ.get("OPENAI_API_KEY"):
        raise ConfigError("OPENAI_API_KEY not set")
        
    options = model.get("options", {}) 
    effort = options.get("effort")
    max_output_tokens = options.get("max_output_tokens", 20000)
    
    client = openai.OpenAI()
    
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
    usage = {"input_tokens": response.usage.input_tokens, "output_tokens": response.usage.output_tokens}

    LOGS_DIR.mkdir(exist_ok=True)
    (LOGS_DIR / f"{call_id}_response.json").write_text(
        response.model_dump_json(indent=2, exclude_none=True),
        encoding="utf-8",
    )
    
    if status != "completed":

        #FAILED_DIR.mkdir(exist_ok=True)
        #(FAILED_DIR / f"{call_id}_response.json").write_text(
        #    response.model_dump_json(indent=2, exclude_none=True),
        #    encoding="utf-8",
        #)
        
        if response.incomplete_details:
            reason = response.incomplete_details.reason
        elif response.error:
            reason = f"{response.error.code}: {response.error.message}"
        else:
            reason = "unknown"
        raise OutputError(f"OpenAI response not completed: status {status}, reason {reason}", usage = usage)
                            
    response = {
        "id": response.id,
        "status": status,
        "output": response.output_text,
        "usage": usage
    }

    return response
