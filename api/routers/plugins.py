from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from plugins.manager import plugin_manager
from plugins.sdk.base import PluginResult

router = APIRouter(prefix="/plugins", tags=["Plugin Platform"])


class InstallPluginRequest(BaseModel):
    plugin_id: str
    config: Optional[Dict[str, Any]] = None


class RemovePluginRequest(BaseModel):
    plugin_id: str


class EnableDisableRequest(BaseModel):
    plugin_id: str


class UpdatePluginRequest(BaseModel):
    plugin_id: str
    config: Optional[Dict[str, Any]] = None


class ExecutePluginRequest(BaseModel):
    plugin_id: str
    action: str
    params: Optional[Dict[str, Any]] = None
    confirmed: Optional[bool] = False


@router.post("/install")
def install_plugin(req: InstallPluginRequest):
    """Installs or activates a plugin from the marketplace catalog."""
    res = plugin_manager.install_plugin(req.plugin_id, req.config)
    if res.get("status") == "error":
        raise HTTPException(status_code=400, detail=res.get("message"))
    return res


@router.post("/remove")
def remove_plugin(req: RemovePluginRequest):
    """Uninstalls and removes a plugin from active registry."""
    success = plugin_manager.uninstall_plugin(req.plugin_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Plugin '{req.plugin_id}' not found.")
    return {"status": "success", "message": f"Plugin '{req.plugin_id}' removed.", "plugin_id": req.plugin_id}


@router.get("/list")
@router.post("/list")
def list_plugins():
    """Lists all registered plugins and marketplace catalog."""
    installed = plugin_manager.list_plugins()
    catalog = plugin_manager.marketplace_catalog
    return {
        "status": "success",
        "count": len(installed),
        "installed_plugins": installed,
        "marketplace_catalog": catalog
    }


@router.post("/update")
def update_plugin(req: UpdatePluginRequest):
    """Updates configuration or reloads a plugin."""
    success = plugin_manager.reload_plugin(req.plugin_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Plugin '{req.plugin_id}' not found.")
    return {"status": "success", "message": f"Plugin '{req.plugin_id}' reloaded.", "plugin_id": req.plugin_id}


@router.post("/enable")
def enable_plugin(req: EnableDisableRequest):
    """Enables a registered plugin."""
    success = plugin_manager.enable_plugin(req.plugin_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Plugin '{req.plugin_id}' not found.")
    return {"status": "success", "message": f"Plugin '{req.plugin_id}' enabled."}


@router.post("/disable")
def disable_plugin(req: EnableDisableRequest):
    """Disables a registered plugin."""
    success = plugin_manager.disable_plugin(req.plugin_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Plugin '{req.plugin_id}' not found.")
    return {"status": "success", "message": f"Plugin '{req.plugin_id}' disabled."}


@router.get("/health")
@router.post("/health")
def health_check():
    """Performs plugin platform health diagnostic check."""
    return plugin_manager.check_health()


@router.post("/execute")
async def execute_plugin(req: ExecutePluginRequest):
    """Executes a plugin action inside security sandbox."""
    res = await plugin_manager.execute_plugin_action(
        plugin_id=req.plugin_id,
        action_name=req.action,
        params=req.params or {},
        confirmed=req.confirmed or False
    )
    return res.model_dump()
