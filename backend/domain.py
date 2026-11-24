from fastapi import APIRouter
from folio_api import router as router_0
from events_api import router as router_1
from drill_api import router as router_2
from runthrough_api import router as router_3
from correction_api import router as router_4
from folio_seed import seed
from folio_worker import run as run_job

router = APIRouter(prefix="/api")
router.include_router(router_0)
router.include_router(router_1)
router.include_router(router_2)
router.include_router(router_3)
router.include_router(router_4)
