# API style guide

This guide matches the NumPy/pandas/scikit-learn documentation style. Use NumPy-style docstrings (via numpydoc) with concise summaries and structured sections.

## General rules

- Start with a one-line summary in the imperative mood.
- Add a blank line, then a short paragraph if more context is needed.
- Prefer type hints in the signature; keep docstring types simple.
- Use consistent section order and headings.
- Keep examples short and focused on a single behavior.

## Recommended section order

1. Parameters
2. Returns
3. Raises
4. See Also
5. Notes
6. Examples

## Parameters

- One entry per parameter.
- Parameter name first, then type.
- Wrap long descriptions to keep lines readable.

## Returns

- Use a short name and type, then a clear description.
- For multiple return values, list each on its own line.

## Raises

- Name the exception and the condition that triggers it.

## See Also

- Link to related functions/classes by import path or current namespace.

## Notes

- Use for implementation details or reasoning that is too heavy for the summary.

## Examples

- Use simple, copy-pasteable examples.
- Prefer doctest-style prompts only when the example can be executed as-is.

## Example docstring

```python
class IOService:
    """Load and persist data with shared IO settings.

    Parameters
    ----------
    base_input_path : str
        Base directory for input files.
    base_output_path : str
        Base directory for output files.

    Attributes
    ----------
    base_input_path : str
        Base directory for input files.
    base_output_path : str
        Base directory for output files.

    Examples
    --------
    >>> service = IOService(base_input_path="data/silver", base_output_path="outputs")
    >>> service.base_input_path
    'data/silver'
    """

    def __init__(self, base_input_path: str, base_output_path: str) -> None:
        self.base_input_path = base_input_path
        self.base_output_path = base_output_path
```
