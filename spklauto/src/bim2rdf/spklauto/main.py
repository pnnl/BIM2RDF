"""
This module contains the function's business logic.
Use the automation_context module to wrap your function in an Automate context helper.
"""
from pydantic import Field, SecretStr
from speckle_automate import (
    AutomateBase,
    AutomationContext,
    execute_automate_function,
)

class FunctionInputs(AutomateBase):
    """These are function author-defined values.

    Automate will make sure to supply them matching the types specified here.
    Please use the pydantic model schema to define your inputs:
    https://docs.pydantic.dev/latest/usage/models/
    """
    # An example of how to use secret values.
    whisper_message: SecretStr = Field(title="This is a secret message")
    forbidden_speckle_type: str = Field(
        title="Forbidden speckle type",
        description=(
            "If a object has the following speckle_type,"
            " it will be marked with an error."),)

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
    #db = engine_run(automate_context)
    # The context provides a convenient way to receive the triggering version.
    version_root_object = automate_context.receive_version()

    #os = RunOutputs(db)
    #shacl = os.shacl_report()
    #shacl = [s for s in shacl]
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
        automate_context.mark_run_success("no errors")
    # If the function generates file results, this is how it can be
    # attached to the Speckle project/model


def engine_run(ctx: AutomationContext):
    pid = ctx.automation_run_data.project_id
    from bim2rdf.speckle.data import Project
    pn = Project(pid).name
    from bim2rdf.engine import Run
    r = Run()
    _ = r.run(project_name=pn)
    return _

class RunOutputs:
    def __init__(self, store) -> None:
        from pyoxigraph import Store
        self.store: Store = store
    
    def mapped(self):
        from bim2rdf.queries import queries
        _ = self.store.query(queries['mapped_and_inferred'])
        from pyoxigraph import serialize, RdfFormat
        # rdflib is nicer though
        from pathlib import Path
        o = Path('mapped_and_inferred.ttl')
        _ = serialize(_, open(o, 'wb'), RdfFormat.TURTLE)
        return o
        #automate_context.store_file_result(_)
    
    def shacl_report(self):
        class Node:
            ns = 'http://www.w3.org/ns/shacl#'
            def __init__(self, term):
                self.term = term
                self.var = self.term
            def __str__(self) -> str:
                return f"<{self.ns}{self.term}>"
        S = Node
        vr = S('ValidationResult')
        fn = S('focusNode')
        rm = S('resultMessage')
        vl = S('value')
        rp = S('resultPath')
        ss = S('sourceShape')  
        sv = S('resultSeverity')
        sc = S('sourceConstraintComponent')
        _ = f"""
        select  {fn.var} {rm.var} {vl.var} {rp.var} {sv.var} {ss.var} where {{
        {vr.var} a {vr}.
        optional {{{vr.var} {fn} {fn.var}}}.
        optional {{{vr.var} {rm} {rm.var}}}.
        optional {{{vr.var} {vl} {vl.var}}}.
        optional {{{vr.var} {rp} {rp.var}}}.
        optional {{{vr.var} {sv} {sv.var}}}.
        optional {{{vr.var} {ss} {ss.var}}}.
        }}
        """
        _ = self.store.query(_)
        return _

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
