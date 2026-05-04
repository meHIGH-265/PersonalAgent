from imports of python modules in alfabetical order
blank line
from imports of local modules in alfabetical order
2 blank lines
global statements (other than if __name__)
2 blank lines
function definitions (2 lines gap between each, other thatn main())
2 blank lines
class definitions (2 lines gap between each)
For each class:
 - write the static methods, the __init__, then the rest of the methods.
 - use __ for every private method
 - 1 line gap between methods

main() function (if any)
if __name__ == '__main__': main()
one blank line

Use type annotations for every variable initialization, parameter and return type.
Use the default types (list, dict etc) before importing from typing what is missing from the default pool of types
Don't use Optionals, use | None instead