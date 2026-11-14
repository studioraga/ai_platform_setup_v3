"""Standard-library tests of offline R05 wheel inventory logic."""
import sys
from pathlib import Path
from zipfile import ZipFile

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'/'qualification'))
from audit_r05_public_api import inventory,compare  # noqa: E402

def test_methods_fields_exports(tmp_path):
    old=tmp_path/'old.whl';new=tmp_path/'new.whl'
    prefix='portable_ai_governance/'
    with ZipFile(old,'w') as z:
        z.writestr(prefix+'__init__.py','from .types import *\n')
        z.writestr(prefix+'types.py','''from dataclasses import dataclass
__all__ = ["Item"]
@dataclass
class Item:
    value: str
    def run(self, x: int = 1) -> str: return self.value
''')
    with ZipFile(new,'w') as z:
        z.writestr(prefix+'__init__.py','from .types import *\n')
        z.writestr(prefix+'types.py','''from dataclasses import dataclass
__all__ = ["Item"]
@dataclass
class Item:
    value: int
    def run(self, x: int = 2) -> str: return str(self.value)
    def extra(self): return None
''')
    a=inventory(old);b=inventory(new);changes=compare(a,b)
    cats={x['category'] for x in changes}
    assert 'methods_changed' in cats
    assert 'methods_added' in cats
    assert 'annotated_fields_changed' in cats
    assert a[prefix+'__init__.py']['star_imports']==[{'module':'types','level':1}]
    assert a[prefix+'types.py']['__all__']==['Item']

def test_removed_exports_are_flagged(tmp_path):
    old=tmp_path/'old.whl';new=tmp_path/'new.whl'
    with ZipFile(old,'w') as z:z.writestr('portable_ai_governance/__init__.py','from .one import Widget\n')
    with ZipFile(new,'w') as z:z.writestr('portable_ai_governance/__init__.py','')
    assert any(x['category']=='imports_removed' for x in compare(inventory(old),inventory(new)))
