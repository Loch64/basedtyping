from typing import Generic, TypeVar

from pytest import raises

from basedtyping.generics import T, T_co, T_cont
from basedtyping.reified_generic import NotReifiedException, ReifiedGeneric

# pylint:disable=no-self-use

T2 = TypeVar("T2")


class Reified(ReifiedGeneric[tuple[T, T2]]):
    ...


class ReifiedList(ReifiedGeneric[tuple[T]], list[T]):
    ...


class Normal(Generic[T, T2]):
    ...


def test_args_and_params() -> None:
    assert (
        Normal[int, str].__args__  # type:ignore[attr-defined,misc]
        == Reified[int, str].__args__
    )
    assert (
        Normal[int, str].__origin__.__parameters__  # type:ignore[attr-defined,misc]
        == Reified[int, str].__origin__.__parameters__  # type:ignore[attr-defined,misc]
    )


def test_reified_list() -> None:
    it = ReifiedList[int]([1, 2, 3]).__orig_class__
    assert it.__origin__ == ReifiedList  # type:ignore[attr-defined,misc]
    assert it.__args__ == (int,)
    assert it.__parameters__ == ()


# https://github.com/KotlinIsland/basedmypy/issues/5
def test_isinstance() -> None:
    assert isinstance(Reified[int, str](), Reified[int, str])  # type:ignore[misc]
    assert not isinstance(Reified[int, str](), Reified[int, int])  # type:ignore[misc]


def test_issubclass() -> None:
    assert issubclass(Reified[int, str], Reified[int, str])  # type:ignore[misc]
    assert not issubclass(Reified[int, str], Reified[int, int])  # type:ignore[misc]


def test_reified_generic_without_generic_alias() -> None:
    with raises(NotReifiedException):
        Reified()  # pylint:disable=no-value-for-parameter


class TestVariance:
    def test_covariant(self) -> None:
        class Foo(ReifiedGeneric[T_co]):
            pass

        assert isinstance(Foo[int](), Foo[int | str])  # type:ignore[misc]
        assert not isinstance(Foo[int | str](), Foo[int])  # type:ignore[misc]

    def test_contravariant(self) -> None:
        class Foo(ReifiedGeneric[T_cont]):
            pass

        assert isinstance(Foo[int | str](), Foo[int])  # type:ignore[misc]
        assert not isinstance(Foo[int](), Foo[int | str])  # type:ignore[misc]

    def test_invariant(self) -> None:
        class Foo(ReifiedGeneric[T]):
            pass

        assert not isinstance(Foo[int](), Foo[int | str])  # type:ignore[misc]
        assert not isinstance(Foo[int | str](), Foo[int])  # type:ignore[misc]
