"""
This module contains the function's business logic.
Use the automation_context module to wrap your function in an Automate context helper.
"""
from pydantic import Field
from speckle_automate import (
    AutomateBase,
    AutomationContext,
    execute_automate_function,
)

class FunctionInputs(AutomateBase):
    models: str = Field(title="csv of models")


def automate_function(
    automate_context: AutomationContext,
    function_inputs: FunctionInputs,
) -> None:
    """This is an example Speckle Automate function.

    Args:
        automate_context: A context-helper object that carries relevant information
            about the runtime context of this function.
            It gives access to the Speckle project data that triggered this run.
            It also has convenient methods for attaching result data to the Speckle model.
        function_inputs: An instance object matching the defined schema.
    """
    # The context provides a convenient way to receive the triggering version.
    version_root_object = automate_context.receive_version()

    # objects_with_forbidden_speckle_type = [
    #     b
    #     for b in flatten_base(version_root_object)
    #     if b.speckle_type == function_inputs.forbidden_speckle_type
    # ]
    # count = len(objects_with_forbidden_speckle_type)

    if True: #count > 0:
        # This is how a run is marked with a failure cause.
        # automate_context.attach_error_to_objects(
        #     category="Forbidden speckle_type"
        #     f" ({function_inputs.forbidden_speckle_type})",
        #     object_ids=[o.id for o in objects_with_forbidden_speckle_type if o.id],
        #     message="This project should not contain the type: "
        #     f"{function_inputs.forbidden_speckle_type}",
        # )
        # automate_context.mark_run_failed(
        #     "Automation failed: "
        #     f"Found {count} object that have one of the forbidden speckle types: "
        #     f"{function_inputs.forbidden_speckle_type}"
        # )

        # # Set the automation context view to the original model/version view
        # # to show the offending objects.
        # automate_context.set_context_view()
        ...
    else:
        automate_context.mark_run_success("No forbidden types found.")
    # If the function generates file results, this is how it can be
    # attached to the Speckle project/model
    #automate_context.store_file_result("./report.pdf")
    #_ = engine_run(automate_context)
    #automate_context.store_file_result(_)
    from pathlib import Path
    _ = Path('223p.ttl')
    assert(_.exists())
    automate_context.store_file_result(_)
    automate_context.mark_run_success("you good")

def engine_run(ctx: AutomationContext):
    pid = ctx.automation_run_data.project_id
    from speckle.data import Project
    pn = Project(pid).name
    from bim2rdf.engine import Run
    r = Run()
    from pathlib import Path
    _ = r.run(
        ontology=Path('223p.ttl'),
        project_name=pn,
        model_name='pritoni 1.ifc', )
    dq = """
        prefix q: <urn:meta:bim2rdf:ConstructQuery:>
        construct {?s ?p ?o.}
        WHERE {
        <<?s ?p ?o>> q:name ?mo.
        filter (CONTAINS(?mo, ".mapping.") || CONTAINS(?mo, ".data.") ) 
        }"""
    _ = _.query(dq)
    from pyoxigraph import serialize, RdfFormat
    # rdflib is nicer though
    o = 'mapped.ttl'
    _ = serialize(_, open(o, 'wb'), RdfFormat.TURTLE)
    return o



def automate_function_without_inputs(automate_context: AutomationContext) -> None:
    """A function example without inputs.

    If your function does not need any input variables,
     besides what the automation context provides,
     the inputs argument can be omitted.
    """
    pass



# make sure to call the function with the executor
if __name__ == "__main__":
    # NOTE: always pass in the automate function by its reference; do not invoke it!
    # Pass in the function reference with the inputs schema to the executor.
    execute_automate_function(automate_function, FunctionInputs)

    # If the function has no arguments, the executor can handle it like so
    # execute_automate_function(automate_function_without_inputs)
