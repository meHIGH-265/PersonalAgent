# --- IMPORTS ----------------------------------------------------

import os
import sys as system
import json, math as m

from pathlib import Path
from math import sin, cos as cosine
from ..module import something, other as other_alias
from .subpkg import (
    A,
    B as Bee,
    C,
)

# --- TOP-LEVEL BLOCK --------------------------------------------

print("This is top-level code")
x = 10
y = [1, 2, 3]

# --- CLASSES -----------------------------------------------------

class Base1:
    pass

class Base2:
    pass

class ComplexClass(Base1,
                   Base2):
    class_attr = 42

    print("class block")

    def method_no_annotations(self, a, b=3):
        print("Inside method_no_annotations")
        return a + b

    def method_with_annotations(self,
                                x: int,
                                y: str = "hello"
                               ) -> bool:
        def nested_in_method(z: float) -> float:
            return z * 2.0
        return isinstance(x, int)

    @staticmethod
    def static_method(a, b):
        return a * b

    async def async_method(self, value: int) -> None:
        return None

# --- MORE COMPLEX FUNCTIONS --------------------------------------

def function_no_annotations(a, b, c=5):
    print(a, b, c)

def function_full_annotations(
    x: int,
    y: str,
    *,
    z: float = 3.14,
    **kwargs
) -> dict:
    return {"x": x, "y": y, "z": z, "rest": kwargs}

def function_with_positional_only(
    a,
    b,
    /,
    c: int,
    d=10,
    *,
    e: str = "abc",
    **kw
) -> None:
    print(a, b, c, d, e, kw)

def outer_function(u: int) -> int:
    def inner_function(v: int) -> int:
        return v * 2
    return inner_function(u)

# --- ASYNC & DECORATED ------------------------------------------

def decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@decorator
async def decorated_async_function(a: int, b=10) -> str:
    return str(a + b)

# --- FINAL BLOCK -------------------------------------------------

for i in range(3):
    print("End block", i)
