"""API 路由包初始化"""

from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["API"])
