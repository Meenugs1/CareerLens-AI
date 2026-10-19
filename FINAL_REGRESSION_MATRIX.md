# CareerLens Final Regression Matrix

Tested with the repository virtual environment, FastAPI `TestClient`, and the current cached dataset.

| Feature | Endpoint | Test input | Status | Notes |
|---|---|---|---|---|
| Recommendation | `POST /recommend` | Data Analyst, Python/SQL, Internship | HTTP 200 | Results and summary returned |
| Recommendation | `POST /recommend` | Data Analyst, Python/SQL, Any job type | HTTP 200 | Existing flow preserved |
| Market Intelligence | `GET /market-intelligence` | role=Data Analyst | HTTP 200 | Dataset overview and breakdowns returned |
| Skill Gap | `POST /skill-gap` | Data Analyst, Python/SQL | HTTP 200 | Coverage and skill evidence returned |
| Career Simulator | `POST /career-simulator` | Data Analyst, add Tableau | HTTP 200 | Before/after result returned |
| Career Switch | `POST /career-switch` | Data Analyst to Data Engineer | HTTP 200 | Overlap and target-role evidence returned |
| Career Path | `GET /career-path` | role=Data Analyst | HTTP 200 | Related roles returned |
| What Can I Become? | `POST /what-can-i-become` | Python/SQL/Excel/Power BI | HTTP 200 | Role matches returned |
| Company Search | `GET /companies` | query=accenture | HTTP 200 | Accenture returned with 8,193 jobs |
| Company Intelligence | `GET /company-intelligence` | company=Accenture | HTTP 200 | Roles, locations, skills, salary, ratings returned |
| Company Intelligence | `GET /company-intelligence` | company=IBM | HTTP 200 | Explicit salary-unavailable state returned |
| Company Intelligence | `GET /company-intelligence` | unknown company | HTTP 200 | Explicit no-data response returned |
| Frontend lint | `npm run lint` | frontend directory | Passed | ESLint exit code 0 |
| Frontend build | `npm run build` | frontend directory | Passed | Vite production build completed |
| Diagnostics | Touched backend/frontend files | Workspace diagnostics | Passed | No reported errors |
| Dataset integrity | `jobs_cleaned.xlsx` | Source file and cache logic | Passed | No dataset source files modified |

## Warm Endpoint Measurements

Measured in one warmed FastAPI process:

- `/recommend` Internship: 0.057 seconds
- `/recommend` Any job type: 0.420 seconds
- `/market-intelligence`: 1.556 seconds
- `/skill-gap`: 0.346 seconds
- `/career-simulator`: 0.008 seconds
- `/career-switch`: 0.325 seconds
- `/career-path`: 0.623 seconds
- `/what-can-i-become`: 0.370 seconds
- `/companies`: 0.151 seconds
- `/company-intelligence`: 0.019 seconds

Market Intelligence is the slowest endpoint because it performs multiple role-level aggregations per request. No request-time Excel reload was observed.
