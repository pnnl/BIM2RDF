"""
just wraps pyshacl to suppress validation errors
"""
from subprocess import run
#python -m pyshacl --shacl ../../test/test.ttl  -f turtle --iterate-rules --advanced -o validation.ttl  inferred.ttl
import sys
r = run(['python', '-m', 'pyshacl'] + list(sys.argv[1:]), shell=True, check=False)

# from pyshacl.errors import  (ConstraintLoadError,
#     ReportableRuntimeError,
#     RuleLoadError,
#     ShapeLoadError,
#     ValidationFailure)
#https://github.com/RDFLib/pySHACL/blob/53d04d65e6ec44e143356019f1d14256c83a7d4f/pyshacl/cli.py#L215
#ValidationError uniquely is exit code 1

if r.returncode in {0, 1}:
    pass
else:
    sys.exit(r.returncode)

