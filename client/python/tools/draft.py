from pathlib import Path


path = 'asd'

absolute_path = Path(path).resolve()

print(absolute_path)

print(absolute_path.__str__())
