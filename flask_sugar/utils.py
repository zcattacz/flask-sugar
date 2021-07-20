import inspect
import typing as t
import re

from pydantic.typing import ForwardRef, evaluate_forwardref


def convert_path(url_rule: str) -> str:
    """
    convert "/api/items/<int:id>/" to "/api/items/{id}/"
    """
    subs = []
    for sub in str(url_rule).split("/"):
        if "<" in sub:
            if ":" in sub:
                start = sub.index(":") + 1
            else:
                start = 1
            subs.append("{{{:s}}}".format(sub[start:-1]))
        else:
            subs.append(sub)
    return "/".join(subs)


def get_path_param_names(path: str) -> t.Set[str]:
    return set(re.findall("{(.*?)}", path))


def get_typed_annotation(
    param: inspect.Parameter, globalns: t.Dict[str, t.Any]
) -> t.Any:
    annotation = param.annotation
    if isinstance(annotation, str):
        annotation = ForwardRef(annotation)
        annotation = evaluate_forwardref(annotation, globalns, globalns)
    return annotation


def get_typed_signature(call: t.Callable) -> inspect.Signature:
    signature = inspect.signature(call)
    globalns = getattr(call, "__globals__", {})
    typed_params = [
        inspect.Parameter(
            name=param.name,
            kind=param.kind,
            default=param.default,
            annotation=get_typed_annotation(param, globalns),
        )
        for param in signature.parameters.values()
    ]
    typed_signature = inspect.Signature(typed_params)
    return typed_signature