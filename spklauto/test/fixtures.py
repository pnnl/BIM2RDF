# removing pytest from
# https://github.com/specklesystems/specklepy/blob/78c55b787f1ebd51df04adcb5971a39627bd1b04/src/speckle_automate/fixtures.py
"""Some useful helpers for working with automation data."""
from dataclasses import dataclass
@dataclass
class TestAutomationEnvironment:
    token: str
    server_url: str
    project_id: str
    automation_id: str
from bim2rdf.core.config import config
testenv = TestAutomationEnvironment(
    token=config.speckle.token,
    server_url=f'https://{config.speckle.server}/',
    project_id=config.speckle.automate.project_id,
    automation_id=config.speckle.automate.automation_id,
)


from speckle_automate.schema import AutomationRunData, TestAutomationRunData
def automation_run(
) -> TestAutomationRunData:
    """Create test run to report local test results to"""
    #https://github.com/specklesystems/specklepy/blob/6c33c61a6de7032a0f14663efac1770c71f27643/src/speckle_automate/fixtures.py#L58
    _ = """ mutation { projectMutations {
        automationMutations(projectId: "_pid") {
            createTestAutomationRun(automationId: "_aid") {
                automationRunId
                functionRunId
                triggers {
                    payload {
                        modelId
                        versionId
                    }
                    triggerType}}}}}
    """
    _ = _.replace('_pid',     testenv.project_id)
    _ = _.replace('_aid',  testenv.automation_id)
    from bim2rdf.speckle.graphql import query_function
    result = query_function(_, )
    return (
        result.get("projectMutations")
        .get("automationMutations")
        .get("createTestAutomationRun")
    )


def automation_run_data(
) -> AutomationRunData:
    """Create automation run data for a new run for a given test automation"""
    ar = automation_run()
    return AutomationRunData(
        project_id=testenv.project_id,
        speckle_server_url=testenv.server_url,
        automation_id=testenv.automation_id,
        automation_run_id=ar["automationRunId"],
        function_run_id=ar["functionRunId"],
        triggers=ar["triggers"],
    )
