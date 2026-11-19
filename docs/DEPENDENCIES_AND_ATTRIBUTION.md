# Dependencies and attribution

Original first-party Python, HTML, CSS, JavaScript, fixtures, tests and documentation were authored in this run. The projects share original CSS primitives authored for this assignment. No application template, external repository code, logos, stock images or copied dashboard was used. UI screenshots are generated from the local applications. Unicode marks and system fonts require no downloaded font or icon assets.

Resolved packages are pinned in requirements.lock. Runtime/dev packages include FastAPI, Starlette, Pydantic, Uvicorn, SQLAlchemy, Alembic, psycopg, pytest and HTTPX. PrefLoom adds LangGraph; DeltaIndex adds Redis and pgvector clients with optional Sentence Transformers; EvalTrace adds jsonschema. Playwright is browser-test tooling. Installed package license metadata and notices remain in their distributions; do not strip them when redistributing. There is no first-party LICENSE pending owner selection. Docker base images and PostgreSQL/Redis retain their own licenses. Optional model weights require review of their model card/license before distribution.

Official documentation consulted for API patterns:
- https://reference.langchain.com/python/langgraph/graph/state/StateGraph
- https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html

No nontrivial tutorial implementation was copied. This list is not a legal audit; consult each installed distribution's license files. A generated package inventory is recorded in dependencies.json when available.
