from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage 
from langchain_core.messages import ToolMessage
from langchain_core.messages import SystemMessage 
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from pydantic import Field, BaseModel
from dotenv import load_dotenv

from django.core.mail import send_mail
from django.conf import settings

load_dotenv()

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    loudness_Data: str
    Sharpness_Data: str

    # output data 
    agent_response: str
    agent_action: str
    gearbox_status: str
    inform_engineer_email: str
    request_maintenance_email: str

@tool 
def inform_engineer(informMessage: str) -> str:
    """Tool for informing the engineer about the gearbox condition."""
    
    return send_mail('Gearbox Condition Alert', 
                     informMessage, 
                     settings.EMAIL_HOST_USER,
                     ['shervindeptest1@gmail.com'],
                     fail_silently=False
                     )

@tool
def request_maintenance(requestMessage: str) -> str:
    """Tool for submitting a maintenance request for a gearbox issue if it is not Healthy."""
  
    return send_mail('URGENT! Maintenance Request', 
                     requestMessage, 
                     settings.EMAIL_HOST_USER,
                     ['shervindeptest1@gmail.com'],
                     fail_silently=False
                     )


tools = [inform_engineer, request_maintenance]

llm = ChatOpenAI(model_name="gpt-4", temperature=0)
llm_with_tools = ChatOpenAI(model_name="gpt-4o", temperature=0).bind_tools(tools)

class AgentResponseModel(BaseModel):
    agent_response: str = Field(
        description="A general response regard what the results shows and what the model predicts the Gearbox condition to be"
    )
    agent_action: str = Field(
        description="If the Gearbox condition is not healthy, recommend some actions to be taken. Else just return No Action needed"
    )
    gearbox_status: str = Field(
        description="Return JUST the gearbox status based on the result from one of the following (gearbox_conditions = 'Broken', 'Missing Tooth', 'Healthy','Root Crack', 'Wear')"

    )
    inform_engineer_email: str = Field(
        description="Since you are the end of the pipeline, create for me an email response to inform the senior Engineer that the analysis is complete, the results and gearbox condition"
    )
    request_maintenance_email: str = Field(
        description="Craft an email to the maintenance team IF the gearbox status is not healthy, else you can just return None."
    )

def analysis_agent(state: AgentState) -> AgentState:
    """ Agent does analysis of results and generates response first """

    system_prompt = SystemMessage(
        content=f"""
        You are my AI Inspection Engineer Asisstant. vibration data from gearboxes was collected and fed into matlab for
        psychoacoustic parameters sharpness and Loudness. Thereafter these samples were predicted 
        from two different established 1D CNN models for both sharpness and Loudness. 

        Results for the predicted Gearbox conditions are here, the majority number is what the condition high likely is
        Loudness: {state["loudness_Data"]}
        Sharpness: {state["Sharpness_Data"]}

        I want you to craft for me the responses as follows: 
        1. A general response regard what the results shows and what the model predicts the Gearbox condition to be 
        2. If the Gearbox condition is not healthy, recommend some actions to be taken. Else just return No Action needed
        3. Return JUST the gearbox status based on the result from one of the following (gearbox_conditions = 'Broken', 'Missing Tooth', 'Healthy','Root Crack', 'Wear')
        4. Since you are the end of the pipeline, create for me an email response to inform the senior Engineer that the analysis is complete, the results and gearbox condition
        5. Craft an email to the maintenance team IF the gearbox status is not healthy, else you can just return None. 
        
        """
        )
    
    response = llm.with_structured_output(AgentResponseModel).invoke([system_prompt])

    state["agent_response"] = response.agent_response
    state["agent_action"] = response.agent_action
    state["gearbox_status"] = response.gearbox_status
    state["inform_engineer_email"] = response.inform_engineer_email
    state["request_maintenance_email"] = response.request_maintenance_email

    return state


def contact_agent(state: AgentState) -> AgentState:
    system_prompt = SystemMessage(
        content=f"""
            You are my Contact Engineer. Your job is to take a look at the gearbox condition, and the emails drafted
            by the analysis agent, and help me call the relevant tools for contacting and passing the email messasge to the tool.

            gearbox stats: {state["gearbox_status"]}
            inform_engineer_email: {state["inform_engineer_email"]}
            request_maintenance_email: {state["request_maintenance_email"]}


            Call the inform_engineer to alert the engineer as always 
            Only call the request_maintenance tool if the condition of the gearbox is NOT Healthy! 
        """
    )
    response = llm_with_tools.invoke([system_prompt] + state["messages"])
    return {"messages":[response]}

def should_continue(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]
    if not last_message.tool_calls:
        return "end"
    else:
        return "continue"

graph = StateGraph(AgentState)
graph.add_node("analysis_agent", analysis_agent)
graph.add_node("contact_agent", contact_agent)
tool_node = ToolNode(tools=tools)
graph.add_node("tools", tool_node)

graph.set_entry_point("analysis_agent")
graph.add_edge("analysis_agent", "contact_agent")

graph.add_conditional_edges(
    "contact_agent",
    should_continue,
    {
        "continue":"tools",
        "end":END
    }
)

graph.add_edge("tools", "contact_agent")

app = graph.compile()


    