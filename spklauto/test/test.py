"""Run integration tests with a speckle server."""
from speckle_automate import (
    AutomationContext,
    AutomationStatus,
    run_function
)
from bim2rdf_spklauto.main import FunctionInputs, automate_function
import fixtures as f


def test():
    """Run an integration test for the automate function."""
    automation_context = AutomationContext.initialize(
        f.automation_run_data(), f.testenv.token
    )
    from pydantic import SecretStr
    automate_sdk = run_function(
        automation_context,
        automate_function,
        FunctionInputs(
            whisper_message=SecretStr("sdfsdsdf"),
            forbidden_speckle_type="sdfsd",
        ),
    )
    assert automate_sdk.run_status == AutomationStatus.SUCCEEDED


if __name__ == '__main__':
    test()
