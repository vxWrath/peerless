from typing import TYPE_CHECKING

from litestar.datastructures import State as BaseState

if TYPE_CHECKING:
    from ..cache import Cache
    from ..database import Database

__all__ = (
    'PeerlessState',
)

class PeerlessState(BaseState):
    cache: 'Cache[None]'
    database: 'Database'