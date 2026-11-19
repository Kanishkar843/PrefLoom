from typing import TypedDict, Literal
from pydantic import BaseModel, ConfigDict, Field
from langgraph.graph import StateGraph, START, END

JOBS=[{'id':str(i),'title':title,'company':f'Synthetic Studio {i}','location':location,'skills':skills,'synthetic':True} for i,(title,location,skills) in enumerate([
('Python Backend Engineer','Remote',['python','sql','fastapi']),('Data Engineer','Bengaluru',['python','sql','pipelines']),('Frontend Engineer','Remote',['typescript','react']),('ML Platform Engineer','Hyderabad',['python','docker','ml']),('API Engineer','Remote',['python','fastapi','postgresql'])],1)]
class ToolCall(BaseModel):
    model_config=ConfigDict(extra='forbid')
    name: Literal['search_opportunities','compare_roles','save_preference','update_profile','explain_recommendation']
    query: str=Field(default='',max_length=2000)
    key: str=Field(default='',max_length=64)
    value: str=Field(default='',max_length=500)
class ToolResult(BaseModel):
    mode: Literal['deterministic-offline']='deterministic-offline'
    tool: str
    message: str
    jobs: list[dict]=Field(default_factory=list)
    proposal: dict|None=None
    trace: list[str]
class State(TypedDict,total=False):
    text: str
    memory: dict
    call: dict
    result: dict
    trace: list[str]
def parse(s):
    text=s['text'].strip(); lower=text.lower()
    # Strict commands are data, never executable instructions or arbitrary tool names.
    if lower.startswith('/remember ') and '=' in text:
        key,value=text[10:].split('=',1)
        call=ToolCall(name='save_preference',key=key.strip(),value=value.strip())
    elif lower.startswith('/profile '): call=ToolCall(name='update_profile',value=text[9:])
    elif lower.startswith('/compare'): call=ToolCall(name='compare_roles',query=text[8:].strip())
    elif lower.startswith('/explain'): call=ToolCall(name='explain_recommendation',query=text[8:].strip())
    else: call=ToolCall(name='search_opportunities',query=text)
    return {'call':call.model_dump(),'trace':['parse_intent: strict deterministic commands']}
def retrieve(s): return {'trace':s['trace']+['retrieve_memory: SQL scoped to authenticated user']}
def execute(s):
    c=ToolCall.model_validate(s['call']); proposal=None
    words=set(c.query.lower().split()); preferences=set(' '.join(s['memory'].values()).lower().split())
    ranked=sorted(JOBS,key=lambda j:(-len((words|preferences)&set((' '.join(j['skills'])+' '+j['location']+' '+j['title']).lower().split())),j['id']))
    message='Synthetic opportunities ranked by explicit keyword and saved-preference overlap.'
    if c.name=='save_preference':
        if not c.key or not c.value: raise ValueError('Use /remember key=value with nonempty values')
        proposal={'action':c.name,'payload':{'key':c.key,'value':c.value}}; message='Preference change needs your approval.'; ranked=[]
    elif c.name=='update_profile': proposal={'action':c.name,'payload':{'summary':c.value}}; message='Profile change needs your approval.'; ranked=[]
    elif c.name=='compare_roles': ranked=ranked[:2]; message='Compare the skills and locations of these two synthetic roles.'
    elif c.name=='explain_recommendation': message='Ranking uses exact token overlap with your query and stored preferences; ties use job ID. This is not an LLM judgement.'
    return {'result':{'tool':c.name,'message':message,'jobs':ranked,'proposal':proposal,'trace':s['trace']+['choose_typed_tool','execute_read_or_propose_write']}}
def validate(s):
    result=ToolResult.model_validate(s['result']); result.trace+=['validate_output: Pydantic','approval_boundary: writes deferred','respond']
    return {'result':result.model_dump()}
builder=StateGraph(State)
for name,fn in [('parse',parse),('retrieve',retrieve),('execute',execute),('validate',validate)]: builder.add_node(name,fn)
builder.add_edge(START,'parse'); builder.add_edge('parse','retrieve'); builder.add_edge('retrieve','execute'); builder.add_edge('execute','validate'); builder.add_edge('validate',END)
graph=builder.compile()
