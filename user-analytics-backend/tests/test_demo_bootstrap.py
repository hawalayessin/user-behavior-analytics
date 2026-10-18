import pytest
from scripts.init_demo_database import require_disposable_database


@pytest.mark.parametrize("url,confirmed", [
    ("postgresql://user:pass@localhost/customer_data", True),
    ("postgresql://user:pass@localhost/analytics_demo", False),
    ("sqlite:///analytics_demo", True),
])
def test_bootstrap_refuses_non_disposable_or_unconfirmed_targets(url, confirmed):
    with pytest.raises(ValueError):
        require_disposable_database(url, confirmed)


def test_bootstrap_accepts_explicitly_confirmed_demo_target():
    require_disposable_database("postgresql://user:pass@localhost/analytics_demo", True)
