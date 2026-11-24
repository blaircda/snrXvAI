import anthropic, os
from degenerate.errors import GenerationError, TransientError, ConfigError, OutputError 

def call_anthropic(model, sys_input, txt_input):
    """
    Wraps a simple prompt of an Anthropic model
    """
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise ConfigError("ANTHROPIC_API_KEY not set")

    options = model.get("options", {}) 
    effort = options.get("effort")
    max_output_tokens = options.get("max_output_tokens", 20000)
    
    client = anthropic.Anthropic()

    kwargs = {
        "model":  model["name"],
        "system": sys_input,
        "max_tokens": max_output_tokens,
        "messages":[{"role": "user", "content": txt_input}],
    }
    if effort is not None:
        kwargs["output_config"] = {"effort": effort}

    try:
        with client.messages.stream(**kwargs) as stream:
            response = stream.get_final_message()
    except (anthropic.BadRequestError, anthropic.AuthenticationError, anthropic.NotFoundError, anthropic.PermissionDeniedError) as e:
        # 400, 401, 403, 404
        raise ConfigError(f"Anthropic {type(e).__name__}: {e}") from e
    except (anthropic.ConflictError, anthropic.RateLimitError, anthropic.InternalServerError, anthropic.APIConnectionError)  as e:
        # 409, 429, 5xx, connection errors
        raise TransientError(f"Anthropic {type(e).__name__}: {e}") from e
    except anthropic.APIError as e:
        # anything else
        raise GenerationError(f"Anthropic {type(e).__name__}: {e}") from e
                    
    status = response.stop_reason
    #thought_tokens = interaction.usage.total_thought_tokens
    #anthropic does not track thinking tokens
    output_tokens = response.usage.output_tokens

    if status != "end_turn":
        # to do: log failure interactions
        # interaction.to_dict()
        #print(interaction.to_json())
        raise OutputError(f"Anthropic stop reason {status}, total output tokens {output_tokens}")

    output = ""
    for block in response.content:
        if block.type == "text":
            output += block.text
                    
    response = {
        "id": response.id,
        "status": status,
        "output": output,
        "thought_tokens": 0, # set to zero and we will just report total thinking+output for other models
        "output_tokens": output_tokens
    }

    return response
