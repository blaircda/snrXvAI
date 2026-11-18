# define some error classes
class GenerationError(Exception): 
    """Paper generation failed"""
class TransientError(GenerationError):
    """Temporary failure: retry"""
class ConfigError(GenerationError):    
    """Gave wrong input to model calls: do not retry"""
class OutputError(GenerationError):
    """Output returned is unusable"""
