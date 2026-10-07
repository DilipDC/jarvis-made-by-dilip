from jarvis_app.web.research import WebResearchAgent

class FakeSearch:
    def search(self,q):
        return {"results":[{"title":"Example","url":"https://example.com"}]}

def test_research_returns_source_on_fetch_failure():
    result=WebResearchAgent(FakeSearch(),timeout=0.001,max_results=1).research("test")
    assert result["intent"]=="web_research"
    assert result["sources"][0]["title"]=="Example"
