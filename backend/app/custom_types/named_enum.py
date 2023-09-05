# taken from https://github.com/pydantic/pydantic/discussions/2980#discussioncomment-1006430

from enum import Enum

import pydantic.json

class EnumByName(Enum):
   """A custom Enum type for pydantic to validate by name.
   """
   # The reason for this class is there is a disconnect between how
   # SQLAlchemy stores Enum references (by name, not value; which is
   # also how we want our REST API to exchange enum references, by
   # name) and Pydantic which validates Enums by value.  We create a
   # Pydantic custom type which will validate an Enum reference by
   # name.

   # Ugliness: we need to monkeypatch pydantic's jsonification of Enums
   pydantic.json.ENCODERS_BY_TYPE[Enum] = lambda e: e.name

   @classmethod
   def __get_validators__(cls):
      # yield our validator
      yield cls._validate

   @classmethod
   def __modify_schema__(cls, schema):
      """Override pydantic using Enum.name for schema enum values"""
      schema['enum'] = list(cls.__members__.keys())

   @classmethod
   def _validate(cls, v):
      """Validate enum reference, `v`.  

      We check:
        1. If it is a member of this Enum
        2. If we can find it by name.
      """
      # is the value an enum member?
      try:
         if v in cls:
            return v
      except TypeError:
         pass

      # not a member...look up by name
      try:
         return cls[v]
      except KeyError:
         name = cls.__name__
         expected = list(cls.__members__.keys())
         raise ValueError(f'{v} not found for enum {name}. Expected one of: {expected}')

class EnumByValue(Enum):
   """A custom Enum type for pydantic to validate by value.
   """
   # The reason for this class is there is a disconnect between how
   # SQLAlchemy stores Enum references (by name, not value; which is
   # also how we want our REST API to exchange enum references, by
   # name) and Pydantic which validates Enums by value.  We create a
   # Pydantic custom type which will validate an Enum reference by
   # name.

   # Ugliness: we need to monkeypatch pydantic's jsonification of Enums
   pydantic.json.ENCODERS_BY_TYPE[Enum] = lambda e: e.value

   @classmethod
   def __get_validators__(cls):
      # yield our validator
      yield cls._validate

   @classmethod
   def __modify_schema__(cls, schema):
      """Override pydantic using Enum.value for schema enum values"""
      schema['enum'] = list(cls.__members__.values())

   @classmethod
   def _validate(cls, v):
      """Validate enum reference, `v`.  

      We check:
        1. If it is a member of this Enum
        2. If we can find it by name.
      """
      # always look up by name
      try:
         return v in cls
      except KeyError:
         name = cls.__name__
         expected = list(cls.__members__.values())
         raise ValueError(f'{v} not found for enum {name}. Expected one of: {expected}')
