# CareerLens Interview Notes

## 1. Problem Statement

CareerLens helps a job seeker inspect job-market evidence across roles, skills, locations, salaries, and represented companies without presenting unsupported career or hiring guarantees.

## 2. What Makes It Different

It is more than a job list. It combines recommendation scoring with descriptive market analysis, target-role skill gaps, what-if comparisons, career-switch evidence, observed role relationships, skill-based role matches, and company-level dataset evidence.

## 3. Dataset

The backend uses `data/processed/jobs_cleaned.xlsx` and its validated pickle cache. The current working dataset contains 97,682 job records in the tested environment.

## 4. Architecture

The FastAPI app in `backend/main.py` routes requests to focused service modules. The React/Vite frontend uses state-based navigation in `App.jsx` and calls the API directly. No router, database, external company API, or scraper is used.

## 5. Backend Architecture

`recommendation_service.py` owns dataset loading, source-timestamp cache validation, skill aliases, normalization, and recommendation scoring. Other services reuse those helpers and keep feature-specific analysis separate.

## 6. Frontend Architecture

`Header.jsx` changes `activeView` in `App.jsx`. Each feature is a focused component with local loading, error, input, and result state. Shared visual patterns live in `App.css`.

## 7. Recommendation Algorithm

Recommendations retain the existing V4.2-style scoring: skill match, role relevance, experience, location, work mode, freshness, and seniority/fresher handling. This final audit did not change the scoring formula.

## 8. Skill Normalization

Skills are lowercased, aliases such as PowerBI to Power BI and React.js to React are applied, and generic ignored terms are removed. Job matches use normalized skill sets.

## 9. Market Intelligence

Market Intelligence aggregates observed roles, locations, companies, skills, experience buckets, salary records, and related titles for the selected role or the full dataset.

## 10. Skill Gap

Skill Gap compares a normalized user skill set with skill counts from jobs whose titles contain the selected role. Its coverage metric is the percentage of target-role jobs containing at least two selected skills.

## 11. Career Simulator

Career Simulator compares matching-job counts before and after adding one normalized skill for a target role. It uses the existing two-skill match rule and reports descriptive changes only.

## 12. Career Switch

Career Switch compares current normalized skills with the top observed skills in a selected target role and reports overlap, missing skills, and target-role coverage.

## 13. Career Path

Career Path ranks related observed titles using shared normalized key skills and title-token similarity. It limits duplicate seniority families and explicitly avoids guaranteed progression claims.

## 14. What Can I Become?

This feature groups dataset jobs by title family and returns role families where at least two selected normalized skills occur in a job. It reports matching jobs, role totals, match percentage, matching skills, and common missing skills.

## 15. Company Intelligence

Company Intelligence indexes actual company names, IDs, titles, locations, normalized skills, salary records, ratings, and review counts. Salary and rating sections clearly distinguish available dataset records from missing data and independent reviews.

## 16. Performance Optimization

Prepared title, role-match, and company indexes are built after dataset loading. Warm measurements in the tested environment were approximately 0.06-1.56 seconds across endpoints; Market Intelligence was the slowest at approximately 1.56 seconds because it performs several aggregations.

## 17. Dataset Caching

The dataframe is loaded once. The pickle cache is accepted only when its stored source modification timestamp matches the Excel source timestamp and its dataframe shape is valid. Otherwise the Excel file is reread and the cache is rebuilt.

## 18. Challenges

The main engineering challenges were reusing one normalized skill vocabulary across multiple services, grouping noisy job titles conservatively, preventing duplicate full-data parsing, and presenting sparse salary/rating fields without implying complete company coverage.

## 19. Testing

The application was tested with FastAPI `TestClient` for all nine endpoint areas, realistic Data Analyst inputs, Accenture, Infosys, IBM, unknown company input, insufficient skills, and duplicate skills. Frontend ESLint and the Vite production build also passed.

## 20. Known Limitations

Dataset-derived role and company evidence does not represent the complete labor market or a company's complete hiring activity. Title-family grouping is heuristic. Salary coverage is sparse for some companies. Market Intelligence remains the slowest warm endpoint and has no dedicated request-result cache.

## 21. Likely Interview Questions

### Why cache the dataframe and indexes?

The dataset is large enough that rereading Excel and reparsing skill strings per request would create unnecessary latency. Startup preparation allows warm requests to reuse normalized structures.

### How do you avoid making career guarantees?

The UI labels results as observed dataset evidence. It reports counts, overlap, and coverage definitions instead of promotion, hiring, success, or employment probabilities.

### What is the recommendation matching rule?

A job must contain at least two normalized selected skills to count as a skill match. Recommendation ranking then applies the existing multi-factor scoring formula.

### How are company ratings handled?

`AggregateRating` and `ReviewsCount` are reported only as dataset-listed numeric values. They are not treated as recommendations or independent company reviews.

### What would you improve next?

I would add automated API and browser interaction tests, then review dataset-specific title normalization rules with representative samples before changing any production methodology.
