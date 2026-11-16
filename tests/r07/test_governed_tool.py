import importlib.util
from pathlib import Path
import pytest
p=Path(__file__).resolve().parents[2]/'labs/r07/governed_tool.py'
s=importlib.util.spec_from_file_location('r07_tool_fixture',p)
m=importlib.util.module_from_spec(s)
import sys
sys.modules[s.name]=m
s.loader.exec_module(m)

def test_authorized_matching_tenant():
    audit=[]
    result=m.execute(m.ToolRequest('a','read_measurement',True,'a'),audit=audit)
    assert result == 'synthetic-measurement'
    assert audit[0]['allowed'] is True

@pytest.mark.parametrize('req',[
    ('a','read_measurement',False,'a'),
    ('a','read_measurement',True,'b'),
    ('a','delete_measurement',True,'a'),
])
def test_denials_are_audited(req):
    audit=[]
    with pytest.raises(m.Denied):
        m.execute(m.ToolRequest(*req), audit=audit)
    assert audit == [{'action':req[1], 'allowed':False,'tenant_match':req[0]==req[3]}]
