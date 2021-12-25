from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # mypy uses typing_extensions by default (Py 3.8); when importing from typing
    # one will get the following error message in mypy:
    #
    #   Incompatible import of "Literal"
    #   (imported name has type "typing_extensions._SpecialForm", local name has type
    #   "typing._SpecialForm")
    from typing_extensions import Literal
else:
    try:
        from typing import Literal
    except ImportError:
        from typing_extensions import Literal  # noqa: F401
