import metrics


def test_non_int_clicks():
    try:
        metrics.ctr(1.5, 2)
    except TypeError:
        pass
    else:
        raise AssertionError("Non int clicks not handled")


def test_non_int_views():
    try:
        metrics.ctr(1, 2.5)
    except TypeError:
        pass
    else:
        raise AssertionError("Non int views not handled")


def test_non_positive_clicks():
    try:
        metrics.ctr(-1, 2)
    except ValueError:
        pass
    else:
        raise AssertionError("Non positive clicks not handled")


def test_non_positive_views():
    try:
        metrics.ctr(0, -1)
    except ValueError:
        pass
    else:
        raise AssertionError("Non positive views not handled")


def test_clicks_greater_than_views():
    try:
        metrics.ctr(3, 2)
    except ValueError:
        pass
    else:
        raise AssertionError("Clicks greater than views not handled")


def test_zero_views():
    try:
        metrics.ctr(0, 0)
    except ZeroDivisionError:
        pass
    else:
        raise AssertionError("Zero views not handled")
