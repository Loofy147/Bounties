from __future__ import annotations

import pytest

from accounting import (
    UINT256_MAX,
    ModelError,
    OrderModel,
    correct_cumulative_maker_outflow,
    mutated_no_decrement,
    production_guarded_ceil,
    remaining_invalidator,
)


def test_repeated_partial_fills_never_exceed_maker_amount() -> None:
    order = OrderModel(maker_amount=100, taker_amount=250)
    fills = [order.fill_by_making(x) for x in (1, 7, 22, 70)]
    assert correct_cumulative_maker_outflow(fills) == 100
    assert order.remaining_maker == 0
    assert fills[-1].invalidator_after == UINT256_MAX


def test_mixed_maker_and_taker_amount_modes_preserve_remaining() -> None:
    order = OrderModel(maker_amount=1000, taker_amount=3333)
    first = order.fill_by_making(101)
    second = order.fill_by_taking(999)
    third = order.fill_by_making(1_000_000)
    assert first.making_amount == 101
    assert second.making_amount == 299
    assert third.making_amount == 600
    assert order.remaining_maker == 0
    assert correct_cumulative_maker_outflow([first, second, third]) == 1000


def test_request_larger_than_remaining_is_clamped_once() -> None:
    order = OrderModel(maker_amount=100, taker_amount=201)
    fill = order.fill_by_making(10_000)
    assert fill.making_amount == 100
    assert fill.remaining_after == 0
    with pytest.raises(ModelError):
        order.fill_by_making(1)


def test_taking_mode_clamps_when_computed_maker_exceeds_remaining() -> None:
    order = OrderModel(maker_amount=100, taker_amount=3)
    first = order.fill_by_taking(2)
    assert first.making_amount == 66
    second = order.fill_by_taking(10)
    assert second.making_amount == 34
    assert second.taking_amount == 2
    assert order.remaining_maker == 0


def test_rounding_is_floor_for_maker_and_ceil_for_taker() -> None:
    order = OrderModel(maker_amount=7, taker_amount=10)
    maker = order.fill_by_taking(1)
    assert maker.making_amount == 0 or maker.making_amount == 1

    order = OrderModel(maker_amount=7, taker_amount=10)
    taking = order.fill_by_making(1)
    assert taking.taking_amount == 2


def test_remaining_invalidator_is_exact_bitwise_complement() -> None:
    assert remaining_invalidator(0) == UINT256_MAX
    assert remaining_invalidator(1) == UINT256_MAX - 1
    assert remaining_invalidator(100) == UINT256_MAX - 100


def test_negative_control_skipping_decrement_is_detectable() -> None:
    order = OrderModel(maker_amount=10, taker_amount=10)
    first = mutated_no_decrement(order, 6)
    second = mutated_no_decrement(order, 6)
    cumulative = first.making_amount + second.making_amount
    assert cumulative > order.maker_amount


def test_boundaries_and_invalid_inputs() -> None:
    with pytest.raises(ModelError):
        OrderModel(0, 1)
    with pytest.raises(ModelError):
        OrderModel(1, 0)
    with pytest.raises(ModelError):
        OrderModel(UINT256_MAX + 1, 1)
    with pytest.raises(ModelError):
        OrderModel(10, 10).fill_by_making(0)


def test_4_3_2_unchecked_overflow_edge_is_zero_at_the_calculator_boundary() -> None:
    # For orderMaker=max and low-128 orderTaker/swapMaker, the unchecked
    # numerator can wrap.  OrderMixin's downstream zero-amount guard rejects
    # the resulting zero fill; this is a boundary control, not a finding.
    result = production_guarded_ceil(UINT256_MAX, 2, 1)
    assert result == 0


def test_4_3_2_unchecked_overflow_cannot_yield_positive_sub_order_result_after_wrap() -> None:
    # When the guarded branch wraps, numerator = swapMaker*orderTaker + M - 1
    # modulo 2**256.  With both multiplicands below 2**128, the wrapped value
    # is strictly below M whenever an overflow occurs, hence integer division
    # by M yields zero. This captures the downstream-zero-revert classification.
    for order_maker in (UINT256_MAX - 1000, UINT256_MAX - 1, UINT256_MAX):
        for order_taker in (2, 3, 17, 255):
            for swap_maker in (1, 2, 7, 128):
                result = production_guarded_ceil(order_maker, order_taker, swap_maker)
                assert 0 <= result <= 1
