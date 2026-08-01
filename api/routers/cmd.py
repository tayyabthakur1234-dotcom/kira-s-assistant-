from fastapi import APIRouter
from api.models import PowerShellRequest, CMDRequest, PythonExecRequest, APIResponse
from system.cmd_executor import command_executor

router = APIRouter(prefix="/cmd", tags=["Command Execution"])

@router.post("/powershell", response_model=APIResponse)
def run_powershell(req: PowerShellRequest):
    """Executes PowerShell script string and captures output."""
    res = command_executor.execute_powershell(script=req.script, timeout_sec=req.timeout_sec)
    return APIResponse(status=res.get("status", "success"), data=res)

@router.post("/cmd", response_model=APIResponse)
def run_cmd(req: CMDRequest):
    """Executes Windows CMD command."""
    res = command_executor.execute_cmd(command=req.command, timeout_sec=req.timeout_sec)
    return APIResponse(status=res.get("status", "success"), data=res)

@router.post("/python", response_model=APIResponse)
def run_python(req: PythonExecRequest):
    """Executes Python 3 inline code script."""
    res = command_executor.execute_python_code(code=req.code, timeout_sec=req.timeout_sec)
    return APIResponse(status=res.get("status", "success"), data=res)
