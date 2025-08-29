import importlib

from pydantic_ai import RunContext

from state import State

from pandas import DataFrame


INSTALL_MAPPING = {}

def import_dependency(
    name: str,
    extra: str = "",
    errors: str = "raise",
):
    """
    Import an optional dependency.

    By default, if a dependency is missing an ImportError with a nice
    message will be raised. If a dependency is present, but too old,
    we raise.

    Args:
        name (str): The module name.
        extra (str): An additional text to include in the ImportError message.
        errors (str): Representing an action to do when a dependency
            is not found or its version is too old.
            Possible values: "raise", "warn", "ignore":
                * raise : Raise an ImportError
                * warn : Only applicable when a module's version is too old.
                  Warns that the version is too old and returns None
                * ignore: If the module is not installed, return None, otherwise,
                  return the module, even if the version is too old.
                  It's expected that users validate the version locally when
                  using ``errors="ignore"`` (see. ``io/html.py``)
        min_version (str): Specify a minimum version that is different from
            the global pandas minimum version required. Defaults to None.

    Returns:
         Optional[module]:
            The imported module, when found and the version is correct.
            None is returned when the package is not found and `errors`
            is False, or when the package's version is too old and `errors`
            is `'warn'`.
    """

    assert errors in {"warn", "raise", "ignore"}

    package_name = INSTALL_MAPPING.get(name)
    install_name = package_name if package_name is not None else name

    msg = (
        f"Missing optional dependency '{install_name}'. {extra} "
        f"Use pip or conda to install {install_name}."
    )
    try:
        module = importlib.import_module(name)
    except ImportError as exc:
        if errors == "raise":
            raise ImportError(msg) from exc
        return None

    return module


def get_plotly_environment(ctx: RunContext[State]) -> dict:
    """
    Returns the environment for the code to be executed.

    Returns (dict): A dictionary of environment variables
    """
    
    env = {
        "pd": import_dependency("pandas"),
        "px": import_dependency("plotly.express"),
        "df": DataFrame(**ctx.deps.sql_query_result.model_dump()),
    }

    return env