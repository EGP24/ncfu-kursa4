from enum import StrEnum


class HandlerDataSource(StrEnum):
    path = 'path'
    """Path параметры"""
    body = 'body'
    """JsonData параметры"""
    query = 'query'
    """QueryString параметры"""
