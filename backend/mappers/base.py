from datetime import datetime
from decimal import Decimal
from typing import Any, Protocol

from serpyco_rs import CustomType, Serializer


class SerializerProtocol(Protocol):
    def serialize(self, obj: Any, **kwargs: Any) -> Any: ...

    def deserialize(self, obj: Any, **kwargs: Any) -> Any: ...



class MapperError(Exception):
    pass


class ValueMapper:
    def serialize(self, value: Any) -> Any:
        return value

    def deserialize(self, value: Any) -> Any:
        return value


class EntityMapper[T: Any]:
    def __init__(
        self,
        entity_type: type[T],
        *,
        without_camelcase: bool = False,
        datetime_mapper: Any | None = None,
        decimal_mapper: Any | None = None,
        **_: Any,
    ) -> None:
        self.entity_type = entity_type
        self.without_camelcase = without_camelcase
        self.datetime_mapper = datetime_mapper
        self.decimal_mapper = decimal_mapper
        self._serializer = self._build_serializer()

    def map_to(self, obj: T) -> Any:
        try:
            return self._serializer.dump(obj)
        except Exception as exc:
            raise MapperError(
                f'Не удалось сериализовать {self.entity_type.__name__}: {exc}'
            ) from exc

    def map_from(self, data: Any) -> T:
        try:
            if isinstance(data, self.entity_type):
                return data

            normalized = self._normalize_input(data)
            return self._serializer.load(normalized)
        except Exception as exc:
            raise MapperError(
                f'Не удалось десериализовать в {self.entity_type.__name__}: {exc}'
            ) from exc

    def maps_from(self, data_list: list[Any]) -> list[T]:
        return [self.map_from(data) for data in data_list]

    def maps_to(self, obj_list: list[T]) -> list[Any]:
        return [self.map_to(obj) for obj in obj_list]

    def _build_serializer(self) -> Serializer[T]:
        datetime_custom_type = self._make_datetime_custom_type(self.datetime_mapper)
        decimal_custom_type = self._make_decimal_custom_type(self.decimal_mapper)

        def custom_type_resolver(tp: type[Any]) -> CustomType[Any, Any] | None:
            if tp is datetime and datetime_custom_type is not None:
                return datetime_custom_type()

            if tp is Decimal and decimal_custom_type is not None:
                return decimal_custom_type()

            return None

        return Serializer(
            self.entity_type,
            custom_type_resolver=custom_type_resolver,
        )

    @staticmethod
    def _make_datetime_custom_type(mapper: SerializerProtocol | None) -> type[CustomType[Any, Any]] | None:
        if mapper is None:
            return None

        if isinstance(mapper, ValueMapper):
            class DatetimePassthroughType(CustomType[datetime, Any]):
                def serialize(self, value: datetime) -> Any:
                    return value

                def deserialize(self, value: Any) -> datetime:
                    return value

                def get_json_schema(self) -> dict[str, Any]:
                    return {}

            return DatetimePassthroughType

        _mapper = mapper

        class DatetimeType(CustomType[datetime, Any]):
            def serialize(self, value: datetime) -> Any:
                return _mapper.serialize(value)

            def deserialize(self, value: Any) -> datetime:
                return _mapper.deserialize(value)

            def get_json_schema(self) -> dict[str, Any]:
                return {'type': 'string', 'format': 'date-time'}

        return DatetimeType

    @staticmethod
    def _make_decimal_custom_type(mapper: SerializerProtocol | None) -> type[CustomType[Any, Any]] | None:
        if mapper is None:
            return None

        if isinstance(mapper, ValueMapper):
            class DecimalPassthroughType(CustomType[Decimal, Any]):
                def serialize(self, value: Decimal) -> Any:
                    return value

                def deserialize(self, value: Any) -> Decimal:
                    return value

                def get_json_schema(self) -> dict[str, Any]:
                    return {}

            return DecimalPassthroughType

        _mapper = mapper

        class DecimalType(CustomType[Decimal, Any]):
            def serialize(self, value: Decimal) -> Any:
                return _mapper.serialize(value)

            def deserialize(self, value: Any) -> Decimal:
                return _mapper.deserialize(value)

            def get_json_schema(self) -> dict[str, Any]:
                return {'type': 'string'}

        return DecimalType

    @classmethod
    def _normalize_input(cls, data: Any) -> Any:
        if isinstance(data, dict):
            return {key: cls._normalize_input(value) for key, value in data.items()}

        if isinstance(data, list):
            return [cls._normalize_input(value) for value in data]

        if isinstance(data, tuple):
            return [cls._normalize_input(value) for value in data]

        if not isinstance(data, dict) and hasattr(data, 'keys') and hasattr(data, 'values'):
            try:
                return {
                    key: cls._normalize_input(value)
                    for key, value in zip(data.keys(), data.values())
                }
            except Exception:
                pass

        asdict_method = getattr(data, '_asdict', None)
        if callable(asdict_method):
            return cls._normalize_input(asdict_method())

        return data
