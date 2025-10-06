from boot.boot_path_initializer import inject_paths; inject_paths()
from core.phase_control import ensure_phase
from core.trace_logger import log_trace_event
REQUIRED_PHASE = 0.4  # minimum allowed
ensure_phase(REQUIRED_PHASE)
log_trace_event("module_import", module=__name__, required_phase=REQUIRED_PHASE)
