from typing import Literal, Callable, TypeAlias


VideoQuality = Literal["1080", "720", "480", "360"]


ProgressCallback: TypeAlias = Callable[[int, int], None]
BatchProgressCallback: TypeAlias = Callable[[int, int, int, int], None]

ProgressCallbackType: TypeAlias = ProgressCallback | None
BatchProgressCallbackType: TypeAlias = BatchProgressCallback | None
