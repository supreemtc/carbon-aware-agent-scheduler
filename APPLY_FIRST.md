# Apply this upgrade safely

## Add

- `backend/gemini_planner.py`
- `tests/test_optimizer_portfolio.py`
- `docs/gemini.md`
- `docs/benchmarking.md`
- `docs/roadmap.md`
- `site/index.html`
- `site/styles.css`
- `site/script.js`
- `site/.nojekyll`
- `.github/workflows/pages.yml`
- `CONTRIBUTING.md`
- `SECURITY.md`
- `CITATION.cff`

## Replace

- `README.md`
- `docs/architecture.md`

## FastAPI Gemini endpoint

Add to `backend/main.py`:

```python
from pydantic import BaseModel
from backend.gemini_planner import plan_from_text
from backend.scheduler import schedule_workflow

class PromptRequest(BaseModel):
    prompt: str

@app.post("/plan-from-prompt", response_model=ExecutionPlan)
def plan_from_prompt(request: PromptRequest) -> ExecutionPlan:
    try:
        workflow = plan_from_text(request.prompt)
        return schedule_workflow(workflow)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini planner error: {e}")
```

Add this to `requirements.txt`:

```text
google-genai>=1.0.0
```

Do not commit `GEMINI_API_KEY`.

## GitHub Pages

After pushing:

1. Repository → Settings → Pages.
2. Set the source to **GitHub Actions**.
3. Push to `main`.
4. Expected project URL:

`https://supreemtc.github.io/carbon-aware-agent-scheduler/`

GitHub Pages supports project sites in the repository that contains the project code.
