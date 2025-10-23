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
    # """These are function author-defined values.
    # Automate will make sure to supply them matching the types specified here.
    # Please use the pydantic model schema to define your inputs:
    # https://docs.pydantic.dev/latest/usage/models/
    # """
    """BIM2RDF inputs"""
    additional_model_names:     str|None = Field(
        default=None,
        title="model names",
        description="(csv)...in addition to triggering model.",)
    # decided not to use this
    # additional_model_versions:  str|None = Field(
    #     default=None,
    #     title="model versions",
    #     description="(csv)...in addition to triggering model.")


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
    intercept_token(automate_context)
    r = run(automate_context, function_inputs)
    
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
    groups = defaultdict(set)
    for s in shacl:
        _ = s['focusNode'].value
        # if you put an id that's not in the view,
        # it will not be 'selectable' but will still show in the results
        if 'speckle' not in _: continue # not a speckle id
        id = _.split('/')[-1]
        if id not in triggering_ids: continue
        lvl =  (s['resultSeverity'].value).lower()
        category = triggering_ids[id]
        groups[(lvl, category , s['resultMessage'].value )].add(id)

    
    def objects(ids):
        from specklepy.objects import Base
        return [Base(id=id) for id in ids]
    for g, ids in groups.items():
        if 'violation' in g[0]:
            errors = True
            automate_context.attach_error_to_objects(   category=g[1], message=g[2], affected_objects=objects(ids))
        elif 'warn' in g[0]:
            automate_context.attach_warning_to_objects( category=g[1], message=g[2], affected_objects=objects(ids))
        else:
            assert('info' in g[0])
            automate_context.attach_info_to_objects(    category=g[1], message=g[2], affected_objects=objects(ids))
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


def run(ctx: AutomationContext, fins: FunctionInputs):
    def parse(csv: str):
        _ = csv.split(',')
        _ = map(lambda v: v.strip(), _)
        _ = (v for v in _ if v) # remove blanks
        _ = frozenset(_)
        return _
    
    def creation_triggers(ctx: AutomationContext):
        pid = ctx.automation_run_data.project_id
        from bim2rdf.speckle.data import Model, Project
        prj = Project(pid)
        r = []
        from speckle_automate.schema import VersionCreationTrigger
        for t in ctx.automation_run_data.triggers:
            if isinstance(t, VersionCreationTrigger):
                _ = t.payload.model_id
                _ = Model(project=prj, id=_)
                r.append(_)
        return r
    
    model_names = parse(fins.additional_model_names) if fins.additional_model_names else set()
    model_names = {m.name for m in creation_triggers(ctx) } | model_names
    model_names = frozenset(model_names)
    
    from bim2rdf.core.engine import Run
    from pyoxigraph import Store
    from pathlib import Path
    if Path('db').exists():
        from shutil import rmtree
        rmtree(Path('db'), ignore_errors=True)
    #           use pid instead of name bc more unique
    pid = ctx.automation_run_data.project_id
    r = Run("",
            project_id=pid,
            model_names=model_names,
             db=Store('db'))
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

        g.parse(_,      format='turtle')
        g.serialize(o,  format='turtle')
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
    return automate_function(automate_context, None)


def intercept_token(ctx: AutomationContext):
    """to put it into bim2rdf config """
    t = ctx._speckle_token
    from bim2rdf.core.config import config
    try:
        if not config.speckle.token:
            config.speckle.token = t
    except AttributeError:
        config.speckle.token = t



# make sure to call the function with the executor
if __name__ == "__main__":
    # NOTE: always pass in the automate function by its reference; do not invoke it!
    # Pass in the function reference with the inputs schema to the executor.
    execute_automate_function(automate_function, FunctionInputs)

    # If the function has no arguments, the executor can handle it like so
    # execute_automate_function(automate_function_without_inputs)
