import os
import time
from constants import constants
from utils.exception import MyError
from constants.jira_issue_category_enum import JiraIssueCategory
from jira import JIRA


class JiraClient:

    def __init__(self):
        self.jira_server = os.environ.get("JIRA_SERVER")
        self.jira_api_token = os.environ.get("JIRA_API_TOKEN")
        if not self.jira_server:
            raise MyError(error_code=500, error_message="JIRA_SERVER environment variable is not set.")
        if not self.jira_api_token:
            raise MyError(error_code=500, error_message="JIRA_API_TOKEN environment variable is not set.")

        self.jira_client = JIRA(server=self.jira_server,
                                basic_auth=(constants.JIRA_EMAIL, self.jira_api_token))

    def create_ticket_and_return_url(self, project_key: str, bug_summary: str, bug_category: str,
                                     user_name: str = None):
        retries = constants.RETRIES_FOR_ASSIGNING_TICKET
        for attempt in range(retries):
            try:
                return self._create_issue(project_key=project_key, bug_summary=bug_summary, bug_category=bug_category,
                                          user_name=user_name)
            except Exception as e:
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    raise MyError(error_code=500,
                                  error_message=f"Failed to create issue after {retries} attempts: {str(e)}")

    def _create_issue(self, project_key: str, bug_summary: str, bug_category: str, user_name: str = None):
        bug_category = bug_category.replace(" ", "_").lower()
        issue_dict = {
            'project': {'key': project_key},
            'summary': bug_summary,
            'issuetype': {'name': JiraIssueCategory.bug.value},
            'labels': [bug_category]  # Add bug_category to the labels
        }
        new_issue = self.jira_client.create_issue(fields=issue_dict)
        if user_name is not None:
            self.jira_client.assign_issue(new_issue.key, user_name)
        issue_url = f"{self.jira_server}/browse/{new_issue.key}"
        return issue_url
