# removing pytest from
# https://github.com/specklesystems/specklepy/blob/78c55b787f1ebd51df04adcb5971a39627bd1b04/src/speckle_automate/fixtures.py
"""Some useful helpers for working with automation data."""
from pydantic_settings import BaseSettings, SettingsConfigDict
class TestAutomationEnvironment(BaseSettings): # TODO remove pydantic_settings and use project's config
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="speckle_",
        extra="ignore",
    )
    from pydantic import Field
    token: str = Field()
    server_url: str = Field()
    project_id: str = Field()
    automation_id: str = Field()
testenv = TestAutomationEnvironment()


from speckle_automate.schema import AutomationRunData, TestAutomationRunData
def automation_run(
) -> TestAutomationRunData:
    """Create test run to report local test results to"""
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
    from speckle.graphql import query
    result = query(_, )
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
