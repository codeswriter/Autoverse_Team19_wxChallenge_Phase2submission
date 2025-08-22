from ibm_watsonx_orchestrate.agent_builder.tools import tool
from ibm_watsonx_orchestrate.agent_builder.connections.types import (
    ConnectionType,
)
import requests
from pydantic import Field, BaseModel
from typing import List


class Issue(BaseModel):
    """
    Represents the details of a Jira issue.
    """
    key: str = Field(..., title="Issue Key")
    status: str = Field(..., title="Status")
    type: str = Field(..., title="Type")
    external_focal: str = Field(..., title="External Focal")
    title: str = Field(..., title="Issue title")
    requestor_name: str = Field(..., title="Requestor Name")
    brief_summary: str = Field(..., title="Brief Summary")
    related_links: str = Field(..., title="Related Links")
    business_justification: str = Field(..., title="Business Justification")
    business_value_planned: float = Field(..., title="Business value planned")
    desired_completion_date: str = Field(..., title="Desired completion date")
    components: List[str] = Field(..., title="Components")


@tool(expected_credentials=[{"app_id": "jira_auth_basic", "type": ConnectionType.BASIC_AUTH}])
def get_jira_initiative(initiativeid_or_key: str):
    """
    Fetch initiative information from jira server based on Key, Type or other filters.

    :returns: List of initiative detailst including Key, Status, Type, Title, 
              Requestor Name, Brief Summary, Related Link, Business Justification, 
              Business Value Planned, Desired Completion Date,  and Components list
    """

    try:
        if initiativeid_or_key:
            api_url = f"https://jsw.ibm.com/rest/api/2/issue/{initiativeid_or_key}"
        else:
            return "Please provide an issue key or ID"

        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()

        desired_completion_date = data['fields']['customfield_18404']
        components = []
        for component in data['fields']['components']:
            components.append(component['name'])

        if data['fields']['customfield_18404'] is None or (isinstance(data['fields']['customfield_18404'], str) and data['fields']['customfield_18404'].strip() == ""):
            desired_completion_date = 'Not defined'

        parts = data['fields']['description'].split(f"\n")
        descriptions = []

        for part in parts:
            if part.strip() != "":
                descriptions.append(part)

        requestor_name = descriptions[0].split(":")[1] if 1 < len(descriptions[0].split(":")) else ""
        brief_summary = descriptions[1].split(":")[1] if 1 < len(descriptions[1].split(":")) else ""
        related_links = descriptions[2].split(":")[1] if 1 < len(descriptions[2].split(":")) else ""

        return Issue(
            key=data['key'],
            status=data['fields']['status']['name'],
            type=data['fields']['issuetype']['name'],
            external_focal=data['fields']['customfield_26500'],
            title=data['fields']['summary'],
            requestor_name=requestor_name,
            brief_summary=brief_summary,
            related_links=related_links,
            business_justification=data['fields']['customfield_11100'],
            business_value_planned=data['fields']['customfield_12514'],
            desired_completion_date=desired_completion_date,
            components=components).model_dump_json()
    except Exception as e:
        return {"Exception": str(e)}
