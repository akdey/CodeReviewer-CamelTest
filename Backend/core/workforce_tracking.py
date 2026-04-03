import asyncio
import logging
from typing import Any, Dict, List, Optional
from camel.societies.workforce.workforce_callback import WorkforceCallback
from camel.societies.workforce.events import (
    AllTasksCompletedEvent,
    LogEvent,
    TaskAssignedEvent,
    TaskCompletedEvent,
    TaskCreatedEvent,
    TaskDecomposedEvent,
    TaskFailedEvent,
    TaskStartedEvent,
    TaskUpdatedEvent,
    WorkerCreatedEvent,
    WorkerDeletedEvent,
)
from core.websocket_manager import ws_manager

logger = logging.getLogger("hacker-society")

class SocketWorkforceCallback(WorkforceCallback):
    """
    A native CAMEL WorkforceCallback that broadcasts every orchestration event
    to the React frontend via WebSockets.
    """
    def __init__(self, loop: asyncio.AbstractEventLoop):
        self.loop = loop

    def _broadcast(self, event_type: str, data: Dict[str, Any]):
        """Helper to safe-dispatch broadcasts to the main event loop."""
        asyncio.run_coroutine_threadsafe(
            ws_manager.broadcast_json(event_type, data),
            self.loop
        )

    def log_message(self, event: LogEvent) -> None:
        # We capture all coordination/strategy logs for the 'basis' of segregation
        self._broadcast("orchestration_event", {
            "subtype": "log",
            "message": event.message,
            "level": event.level,
            "is_rationale": "decompos" in event.message.lower() or "strategy" in event.message.lower()
        })

    def log_task_created(self, event: TaskCreatedEvent) -> None:
        self._broadcast("orchestration_event", {
            "subtype": "task_created",
            "task_id": event.task_id,
            "description": event.description,
            "parent_id": event.parent_task_id
        })

    def log_task_decomposed(self, event: TaskDecomposedEvent) -> None:
        self._broadcast("orchestration_event", {
            "subtype": "task_decomposed",
            "parent_id": event.parent_task_id,
            "subtask_ids": event.subtask_ids
        })

    def log_task_assigned(self, event: TaskAssignedEvent) -> None:
        self._broadcast("orchestration_event", {
            "subtype": "task_assigned",
            "task_id": event.task_id,
            "worker_id": event.worker_id
        })

    def log_task_started(self, event: TaskStartedEvent) -> None:
        self._broadcast("orchestration_event", {
            "subtype": "task_started",
            "task_id": event.task_id,
            "worker_id": event.worker_id
        })

    def log_task_updated(self, event: TaskUpdatedEvent) -> None:
        self._broadcast("orchestration_event", {
            "subtype": "task_updated",
            "task_id": event.task_id,
            "update_type": event.update_type
        })

    def log_task_completed(self, event: TaskCompletedEvent) -> None:
        self._broadcast("orchestration_event", {
            "subtype": "task_completed",
            "task_id": event.task_id,
            "summary": event.result_summary
        })

    def log_task_failed(self, event: TaskFailedEvent) -> None:
        self._broadcast("orchestration_event", {
            "subtype": "task_failed",
            "task_id": event.task_id,
            "error": event.error_message
        })

    def log_worker_created(self, event: WorkerCreatedEvent) -> None:
        self._broadcast("orchestration_event", {
            "subtype": "worker_created",
            "worker_id": event.worker_id,
            "role": event.role
        })

    def log_worker_deleted(self, event: WorkerDeletedEvent) -> None:
        self._broadcast("orchestration_event", {
            "subtype": "worker_deleted",
            "worker_id": event.worker_id
        })

    def log_all_tasks_completed(self, event: AllTasksCompletedEvent) -> None:
        self._broadcast("orchestration_event", {
            "subtype": "all_tasks_completed"
        })
