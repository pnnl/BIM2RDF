"""Run integration tests with a speckle server."""
from speckle_automate import (
    AutomationContext,
    run_function
)
from bim2rdf.spklauto.main import FunctionInputs, automate_function
#from bim2rdf.spklauto.main import automate_function_without_inputs
import fixtures as f


def test():
    """Run an integration test for the automate function."""
    automation_context = AutomationContext.initialize(
        f.automation_run_data(), f.testenv.token
    )
    automate_sdk = run_function(
        automation_context,
        automate_function,
        FunctionInputs(
           additional_model_names="electrical/main panels",
        ),
    )


if __name__ == '__main__':
    test()
