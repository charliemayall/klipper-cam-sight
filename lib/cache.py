"""TTL caching helpers for async Moonraker/Klipper probes."""

from __future__ import annotations

import time
import weakref
from functools import wraps
from typing import Any, Awaitable, Callable, Generic, TypeVar
from weakref import WeakKeyDictionary

T = TypeVar("T")

_CACHE_REGISTRY: dict[str, set[weakref.ref[TtlCache[Any]]]] = {}


def _register_cache(cache_id: str, cache: TtlCache[Any]) -> None:
    refs = _CACHE_REGISTRY.setdefault(cache_id, set())

    def _drop(ref: weakref.ref[TtlCache[Any]], *, cid: str = cache_id) -> None:
        bucket = _CACHE_REGISTRY.get(cid)
        if bucket is None:
            return
        bucket.discard(ref)
        if not bucket:
            _CACHE_REGISTRY.pop(cid, None)

    refs.add(weakref.ref(cache, _drop))


class TtlCache(Generic[T]):
    """Single-slot TTL cache with optional stale read."""

    __slots__ = (
        "_cache_id",
        "_has_value",
        "_stored_at",
        "_ttl_s",
        "_value",
        "__weakref__",
    )

    def __init__(self, ttl_s: float, *, cache_id: str | None = None) -> None:
        self._ttl_s = ttl_s
        self._cache_id = cache_id
        self._value: T | None = None
        self._stored_at = 0.0
        self._has_value = False
        if cache_id is not None:
            _register_cache(cache_id, self)

    def clear(self) -> None:
        self._has_value = False
        self._value = None

    @classmethod
    def invalidate(cls, cache_id: str) -> int:
        """Drop cached values for every slot registered under cache_id."""
        refs = _CACHE_REGISTRY.get(cache_id, set())
        cleared = 0
        for ref in list(refs):
            cache = ref()
            if cache is None:
                continue
            cache.clear()
            cleared += 1
        return cleared

    @classmethod
    def registered_ids(cls) -> frozenset[str]:
        return frozenset(_CACHE_REGISTRY)

    def get_fresh(self) -> T | None:
        if not self._has_value:
            return None
        if time.monotonic() - self._stored_at < self._ttl_s:
            return self._value
        return None

    @property
    def stale(self) -> T | None:
        return self._value if self._has_value else None

    def set(self, value: T) -> T:
        self._value = value
        self._stored_at = time.monotonic()
        self._has_value = True
        return value

    async def get_or_fetch(
        self,
        fetch: Callable[[], Awaitable[T | None]],
        *,
        fallback: Callable[[], T],
    ) -> T:
        fresh = self.get_fresh()
        if fresh is not None:
            return fresh
        value = await fetch()
        if value is not None:
            return self.set(value)
        return fallback()


def _arg_key(args: tuple[Any, ...], kwargs: dict[str, Any]) -> tuple[Any, ...]:
    return (args, tuple(sorted(kwargs.items())))


def ttl_cache(
    ttl_seconds: float,
    *,
    cache_id: str | None = None,
    is_cacheable: Callable[[Any], bool] = lambda _: True,
) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[T]]]:
    """Cache async function results for ttl_seconds. Per-instance for methods."""

    def decorator(fn: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        _instance_stores: WeakKeyDictionary[Any, dict[tuple[Any, ...], TtlCache[T]]] = (
            WeakKeyDictionary()
        )
        _free_store: dict[tuple[Any, ...], TtlCache[T]] = {}

        def _store_for(args: tuple[Any, ...]) -> dict[tuple[Any, ...], TtlCache[T]]:
            owner = args[0] if args else None
            if owner is not None and not isinstance(owner, type):
                return _instance_stores.setdefault(owner, {})
            return _free_store

        @wraps(fn)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            store = _store_for(args)
            key = _arg_key(args, kwargs)
            slot = store.get(key)
            if slot is None:
                slot = TtlCache(ttl_seconds, cache_id=cache_id)
                store[key] = slot
            fresh = slot.get_fresh()
            if fresh is not None:
                return fresh
            result = await fn(*args, **kwargs)
            if not is_cacheable(result):
                slot.clear()
                return result
            return slot.set(result)

        def cache_clear(*args: Any, **kwargs: Any) -> None:
            store = _store_for(args)
            store.pop(_arg_key(args, kwargs), None)

        def cache_clear_owner(owner: Any) -> None:
            _instance_stores.pop(owner, None)

        wrapper.cache_clear = cache_clear  # ty:ignore[unresolved-attribute]    # pyright: ignore[reportAttributeAccessIssue]
        wrapper.cache_clear_owner = cache_clear_owner  # ty:ignore[unresolved-attribute]   # pyright: ignore[reportAttributeAccessIssue]
        return wrapper

    return decorator


def _self_check() -> None:
    demo_a: TtlCache[str] = TtlCache(30.0, cache_id="demo")
    demo_b: TtlCache[str] = TtlCache(30.0, cache_id="demo")
    assert demo_a.set("a") == "a"
    assert demo_b.set("b") == "b"
    assert TtlCache.invalidate("demo") == 2
    assert demo_a.get_fresh() is None
    assert demo_b.get_fresh() is None
    assert "demo" in TtlCache.registered_ids()

    demo_cache: TtlCache[list[str]] = TtlCache(30.0)
    assert demo_cache.get_fresh() is None
    assert demo_cache.set(["FOO"]) == ["FOO"]
    assert demo_cache.get_fresh() == ["FOO"]
    assert demo_cache.stale == ["FOO"]
