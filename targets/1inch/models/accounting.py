"""Independent accounting model for 1inch Limit Order Protocol 4.3.2 H-A1.

This module intentionally does not import production code. It models only the
observable arithmetic/state contract needed to test partial-fill accounting.
"""
from __future__ import annotations

from dataclasses import dataclass

UINT256_MAX = (1 << 256) - 1


class ModelError(ValueError):
    """Invalid model input or impossible fill."""


def u256(value: int) -> int:
    if not isinstance(value, int) or value < 0 or value > UINT256_MAX:
        raise ModelError(f"not a uint256 value: {value!r}")
    return value


def floor_mul_div(a: int, b: int, denominator: int) -> int:
    """Exact Solidity 0.8 checked-style floor(a*b/denominator) reference."""
    u256(a); u256(b); u256(denominator)
    if denominator == 0:
        raise ModelError("division by zero")
    product = a * b
    if product > UINT256_MAX:
        raise OverflowError("uint256 multiplication overflow")
    return product // denominator


def ceil_mul_div(a: int, b: int, denominator: int) -> int:
    """Exact checked-style ceil(a*b/denominator)."""
    u256(a); u256(b); u256(denominator)
    if denominator == 0:
        raise ModelError("division by zero")
    product = a * b
    numerator = product + denominator - 1
    if product > UINT256_MAX or numerator > UINT256_MAX:
        raise OverflowError("uint256 numerator overflow")
    return numerator // denominator


def production_guarded_ceil(order_maker: int, order_taker: int, swap_maker: int) -> int:
    """Model 4.3.2 getTakingAmount arithmetic, including its low-128 unchecked branch.

    The production function uses unchecked arithmetic when swap_maker and
    order_taker are both below 2**128. In that branch arithmetic wraps modulo
    2**256. This helper models that exact arithmetic outcome so downstream
    guards can decide whether the anomaly is security-relevant.
    """
    u256(order_maker); u256(order_taker); u256(swap_maker)
    if order_maker == 0:
        raise ModelError("order maker amount must be non-zero for ceil calculation")
    if ((swap_maker | order_taker) >> 128) == 0:
        numerator = (swap_maker * order_taker + order_maker - 1) & UINT256_MAX
        return numerator // order_maker
    return ceil_mul_div(swap_maker, order_taker, order_maker)


def remaining_invalidator(remaining_maker: int) -> int:
    """Equivalent of RemainingInvalidatorLib.remains for an already-applied fill."""
    return (~u256(remaining_maker)) & UINT256_MAX


@dataclass(frozen=True)
class FillResult:
    requested_maker: int
    making_amount: int
    taking_amount: int
    remaining_before: int
    remaining_after: int
    invalidator_after: int


@dataclass
class OrderModel:
    maker_amount: int
    taker_amount: int
    remaining_maker: int | None = None

    def __post_init__(self) -> None:
        self.maker_amount = u256(self.maker_amount)
        self.taker_amount = u256(self.taker_amount)
        if self.maker_amount == 0 or self.taker_amount == 0:
            raise ModelError("order amounts must be non-zero")
        if self.remaining_maker is None:
            self.remaining_maker = self.maker_amount
        self.remaining_maker = u256(self.remaining_maker)
        if self.remaining_maker > self.maker_amount:
            raise ModelError("remaining maker amount exceeds order maker amount")

    def fill_by_making(self, requested_maker: int) -> FillResult:
        requested_maker = u256(requested_maker)
        if requested_maker == 0:
            raise ModelError("zero maker request")
        making = min(requested_maker, self.remaining_maker)
        taking = ceil_mul_div(making, self.taker_amount, self.maker_amount)
        return self._apply(requested_maker, making, taking)

    def fill_by_taking(self, requested_taker: int) -> FillResult:
        requested_taker = u256(requested_taker)
        if requested_taker == 0:
            raise ModelError("zero taker request")
        making = floor_mul_div(requested_taker, self.maker_amount, self.taker_amount)
        if making > self.remaining_maker:
            making = self.remaining_maker
            taking = ceil_mul_div(making, self.taker_amount, self.maker_amount)
            if taking > requested_taker:
                raise ModelError("taking amount would exceed request")
        else:
            taking = requested_taker
        return self._apply(requested_taker, making, taking)

    def _apply(self, requested: int, making: int, taking: int) -> FillResult:
        if making <= 0 or taking <= 0:
            raise ModelError("zero-value fill")
        before = self.remaining_maker
        if making > before:
            raise ModelError("maker outflow exceeds remaining amount")
        self.remaining_maker = before - making
        return FillResult(
            requested_maker=requested,
            making_amount=making,
            taking_amount=taking,
            remaining_before=before,
            remaining_after=self.remaining_maker,
            invalidator_after=remaining_invalidator(self.remaining_maker),
        )


def correct_cumulative_maker_outflow(results: list[FillResult]) -> int:
    """Return cumulative maker outflow; callers compare against order.maker_amount."""
    return sum(item.making_amount for item in results)


def mutated_no_decrement(order: OrderModel, requested_maker: int) -> FillResult:
    """Negative control: simulate the class of bug that skips remaining decrement."""
    requested_maker = u256(requested_maker)
    making = min(requested_maker, order.remaining_maker)
    taking = ceil_mul_div(making, order.taker_amount, order.maker_amount)
    before = order.remaining_maker
    return FillResult(
        requested_maker=requested_maker,
        making_amount=making,
        taking_amount=taking,
        remaining_before=before,
        remaining_after=before,
        invalidator_after=remaining_invalidator(before),
    )
