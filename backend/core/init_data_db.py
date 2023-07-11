import asyncio
import random

import pandas as pd

from .database import get_session, init_db


async def _init_all_db():
    pass


if __name__ == "__main__":
    asyncio.run(_init_all_db())
