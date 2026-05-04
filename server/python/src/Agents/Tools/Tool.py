class Tool:
    def __init__(self, name: str, description: str, args_schema: dict[str, type]):
        self.name: str = name
        self.description: str = description
        self.args_schema: dict[str, type] = args_schema

    def get_name(self) -> str:
        return self.name

    def get_description(self) -> str:
        return self.description

    def get_args_schema(self) -> dict[str, type]:
        return {k: v for k, v in self.args_schema.items()}

    def get_schema_parameter(self, parameter: str) -> type:
        return self.args_schema.get(parameter) if parameter in self.args_schema else str
