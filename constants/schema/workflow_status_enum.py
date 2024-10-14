from enum import Enum


class WorkflowStatus(Enum):
    in_progress = "IN_PROGRESS"
    completed = "COMPLETED"
    failed = "failed"
