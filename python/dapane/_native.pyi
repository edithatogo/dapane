"""Private native entry point; use the public dapane module for diagnostics."""

__version__: str

class CoreError(Exception): ...

def evaluate_json(request_json: str) -> str: ...
