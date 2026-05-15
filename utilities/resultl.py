from dataclasses import dataclass
from typing import Any, Optional

''' by usinng this class ,we can easity understand is
service in operate perfecty or not,there is not ambigute

'''
@dataclass
class ServiceResult:
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None