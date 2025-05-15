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
    r = run(automate_context)
    
    os = RunOutputs(r.db)
    _ = automate_context.automation_run_data.triggers[0] # speckle only has one trigger now
    _ = _.payload.model_id # version_id
    from bim2rdf.speckle.data import Project
    project = Project(automate_context.automation_run_data.project_id)
    for model in project.models:
        if model.id == _: break
    triggering_ids = os.ids(project_id=project.id, model_name=model.name)
    _ = os.shacl_report()
    variables = [v.value for v in _.variables]
    shacl = list(_)
    errors: bool = False

    from collections import defaultdict
    groups = defaultdict(list)
    for s in shacl:
        _ = s['focusNode'].value
        # if you put an id that's not in the view,
        # it will not be 'selectable' but will still show in the results
        if 'speckle' not in _: continue # not a speckle id
        id = _.split('/')[-1]
        if id not in triggering_ids: continue
        lvl =  (s['resultSeverity'].value).lower()
        category = triggering_ids[id]
        groups[(lvl, category , s['resultMessage'].value )].append(id)
    
    for g, ids in groups.items():
        if 'violation' in g[0]:
            errors = True
            automate_context.attach_error_to_objects(category=g[1], message=g[2], object_ids=ids)
        elif 'warn' in g[0]:
            automate_context.attach_warning_to_objects(category=g[1], message=g[2], object_ids=ids)
        else:
            assert('info' in g[0])
            automate_context.attach_info_to_objects(category=g[1], message=g[2], object_ids=ids)
        automate_context.set_context_view()
    if not errors:
        automate_context.mark_run_success(("no shacl errors in model scope"
                                           " but maybe warnings"))
    else:
        automate_context.mark_run_failed('shacl errors')

    # file attachments    
    _ = os.mapped_and_inferred(project_id=project.id)
    automate_context.store_file_result(_)
    # todo: att shacl report?


def run(ctx: AutomationContext):
    pid = ctx.automation_run_data.project_id
    from bim2rdf.core.engine import Run
    from pyoxigraph import Store
    from pathlib import Path
    if Path('db').exists():
        from shutil import rmtree
        rmtree(Path('db'), ignore_errors=True)
    #           use pid instead of name bc more unique
    r = Run("", project_id=pid, db=Store('db'))
    _ = r.run()
    return r


class RunOutputs:
    def __init__(self, store) -> None:
        from pyoxigraph import Store
        self.store: Store = store

    def ids(self, *, project_id, model_name):
        from bim2rdf.speckle.meta import prefixes
        dp = prefixes.data(project_id=project_id, object_id="")
        mp = prefixes.meta
        sp = prefixes.concept
        _ = f"""
        prefix d: <{dp.uri}>
        prefix s: <{sp.uri}>
        prefix m: <{mp.uri}>
        select distinct ?id ?category where {{
        <<?id s:category  ?category >> m:model_name "{model_name}".
        }}
        """
        _ = self.store.query(_)
        _ = ( (i['id'].value.split('/')[-1],
               i['category'].value)
               for i in _)
        _ = dict(_)
        return _

    from pathlib import Path    
    def mapped_and_inferred(self, o=Path('mapped_and_inferred.ttl'), project_id=None):
        from bim2rdf.core.queries import queries
        _ = self.store.query(queries['mapped_and_inferred'])
        from pyoxigraph import serialize, RdfFormat
        _ = serialize(_, format=RdfFormat.TURTLE)
        # rdflib is nicer though
        from rdflib import Graph
        g = Graph()
        from bim2rdf.core.queries import DefaultSubstitutions
        for p,n in DefaultSubstitutions.dict().items():
            if 'prefix.' in p:
                g.bind(prefix=p.split('.')[-1], namespace=n)
        if project_id:
            from bim2rdf.speckle.meta import prefixes
            dp = prefixes.data(project_id=project_id, object_id="")
            g.bind(prefix=dp.name, namespace=dp.uri)

        g.parse(_, format='turtle')
        g.serialize(o, format='turtle')
        return o
    
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
        select  ?{fn.var} ?{rm.var} ?{vl.var} ?{rp.var} ?{sv.var} ?{ss.var} where {{
                   ?{vr.var}  a          {vr}.
        optional {{?{vr.var} {fn} ?{fn.var}}}.
        optional {{?{vr.var} {rm} ?{rm.var}}}.
        optional {{?{vr.var} {vl} ?{vl.var}}}.
        optional {{?{vr.var} {rp} ?{rp.var}}}.
        optional {{?{vr.var} {sv} ?{sv.var}}}.
        optional {{?{vr.var} {ss} ?{ss.var}}}.
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
