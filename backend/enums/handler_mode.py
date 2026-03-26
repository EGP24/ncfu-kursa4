from enum import StrEnum


class HandlerMode(StrEnum):
    http = 'http'
    """HTTP мод"""
    ws = 'ws'
    """WebSocket мод"""
