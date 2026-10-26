const {test}=require('node:test');
const assert=require('node:assert/strict');
const {execFileSync}=require('node:child_process');
const vm=require('node:vm');
const source=execFileSync('python3',['-c',
  "import ast,pathlib; t=ast.parse(pathlib.Path('outreach_reply_check_worker.py').read_text()); f=next(n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='_active_thread_profile_url'); print(next(n.args[0].value for n in ast.walk(f) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='evaluate'))"
],{encoding:'utf8'});
const extract=vm.runInNewContext('('+source+')',{URL,location:{href:'https://www.linkedin.com/messaging/thread/test/'}});

function links(rows){
  const outer={}; const scope={parentElement:outer,querySelectorAll(){return anchors;}};
  const anchors=rows.map(row=>({href:row.url,className:'',parentElement:row.own?{className:'msg-s-message-group--is-me',parentElement:scope}:scope,
    getClientRects(){return row.hidden?[]:[1];},
    closest(selector){return {side:row.sidebar,body:row.body,history:row.history,authors:row.author,nav:row.nav}[selector]?{}:null;},
    matches(){return false;},querySelector(selector){return selector==='authors'&&row.author?{}:null;}}));
  return Array.from(extract(scope,{sidebar:'side',bodies:'body',history:'history',authors:'authors'}),r=>({url:r.url,kind:r.kind}));
}
test('sidebar participant links do not contaminate active conversation URL',()=>{
  assert.deepEqual(links([{url:'https://linkedin.com/in/maria/',sidebar:true},
                          {url:'https://linkedin.com/in/oleg/'}]),[{url:'https://linkedin.com/in/oleg/',kind:'header'}]);
});
test('outgoing author profile is excluded without comparing account display names',()=>{
  assert.deepEqual(links([{url:'https://linkedin.com/in/valerie/',history:true,author:true,own:true},
                          {url:'https://linkedin.com/in/oleg/',history:true,author:true}]),
                         [{url:'https://linkedin.com/in/oleg/',kind:'author'}]);
});
test('profile links mentioned inside message bodies are not recipient evidence',()=>{
  assert.deepEqual(links([{url:'https://linkedin.com/in/mentioned/',body:true}]),[]);
});
test('navigation profile and hidden popup links are excluded',()=>{
  assert.deepEqual(links([{url:'https://linkedin.com/in/me/',nav:true},
                          {url:'https://linkedin.com/in/stale/',hidden:true}]),[]);
});
test('company URLs can be identified and skipped without reading history',()=>{
  assert.deepEqual(links([{url:'https://linkedin.com/company/golden-gate/?trk=x'}]),
                         [{url:'https://linkedin.com/company/golden-gate/',kind:'header'}]);
});
test('external hosts and messaging URLs cannot become member identities',()=>{
  assert.deepEqual(links([{url:'https://evil.test/in/oleg/'},
                          {url:'https://linkedin.com/messaging/thread/123/'}]),[]);
});
