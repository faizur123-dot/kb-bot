from enum import Enum


class CurrentState(Enum):

    slack_service = "SLACK_SERVICE"
    llm_service = "LLM_SERVICE"
    jira_service = "JIRA_SERVICE"
    driver_service = "DRIVER_SERVICE"

