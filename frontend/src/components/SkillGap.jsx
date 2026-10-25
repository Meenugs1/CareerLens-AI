import API_URL from "../config/api.js";
import { useState } from "react";
import { parseSkillInput } from "../utils/skillInput";


function SkillGap() {
  const [role, setRole] = useState("");
  const [skills, setSkills] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (event) => {
    event.preventDefault();
    const skillList = parseSkillInput(skills);

    if (!role.trim() || skillList.length === 0) {
      setError("Enter a target role and at least one current skill.");
      setAnalysis(null);
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await fetch(`${API_URL}/skill-gap`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ role: role.trim(), skills: skillList }),
      });

      if (!response.ok) {
        throw new Error(`Server returned ${response.status}`);
      }

      const data = await response.json();
      if (!data.success) {
        throw new Error("Skill Gap request failed.");
      }

      setAnalysis(data);
    } catch (requestError) {
      console.error(requestError);
      setAnalysis(null);
      setError(
        "Unable to load Skill Gap Analysis. Make sure FastAPI is running on port 8000."
      );
    } finally {
      setLoading(false);
    }
  };

  const hasJobs = analysis?.summary?.target_role_jobs > 0;

  return (
    <section className="skill-gap-page">
      <div className="skill-gap-hero">
        <div>
          <p className="market-eyebrow">Evidence from target-role listings</p>
          <h2>Skill Gap Analyzer</h2>
          <p>
            Compare your current skills with the skills appearing in relevant
            job listings. Demand signals describe observed postings, not hiring guarantees.
          </p>
        </div>

        <form className="skill-gap-form" onSubmit={handleSubmit}>
          <label htmlFor="skill-gap-role">Target role</label>
          <input
            id="skill-gap-role"
            value={role}
            onChange={(event) => setRole(event.target.value)}
            placeholder="e.g. Data Analyst"
          />
          <label htmlFor="skill-gap-skills">Current skills</label>
          <input
            id="skill-gap-skills"
            value={skills}
            onChange={(event) => setSkills(event.target.value)}
            placeholder="Python, SQL, Excel"
          />
          <button type="submit" disabled={loading}>
            {loading ? "Analyzing..." : "Analyze Skill Gap"}
          </button>
        </form>
      </div>

      {loading && (
        <div className="market-state" role="status" aria-live="polite">
          <div className="spinner"></div>
          <p>Comparing your skills with target-role listings...</p>
        </div>
      )}

      {error && (
        <div className="error" role="alert">
          {error}
        </div>
      )}

      {!loading && analysis && !hasJobs && (
        <div className="market-state">
          <h3>Insufficient data available</h3>
          <p>No matching target-role jobs were found in the dataset.</p>
        </div>
      )}

      {!loading && analysis && hasJobs && (
        <>
          <section className="market-section">
            <div className="market-section-heading">
              <div>
                <p className="market-eyebrow">Coverage snapshot</p>
                <h3>{analysis.role}</h3>
              </div>
              <span className="market-count">
                {analysis.summary.target_role_jobs.toLocaleString()} analyzed jobs
              </span>
            </div>
            <div className="market-metric-grid skill-gap-metrics">
              <Metric label="Matching jobs" value={analysis.matching_jobs.toLocaleString()} />
              <Metric label="Skill coverage" value={`${analysis.skill_coverage}%`} />
              <Metric label="Matched skills" value={analysis.summary.matched_skill_count} />
              <Metric label="Missing skills" value={analysis.summary.missing_skill_count} />
            </div>
            <p className="skill-gap-definition">{analysis.skill_coverage_definition}</p>
          </section>

          <div className="skill-gap-columns">
            <SkillList
              title="Skills you have"
              subtitle="Skills found in the selected target-role listings."
              items={analysis.matched_skills}
              tone="matched"
            />
            <SkillList
              title="Skills to explore"
              subtitle="Skills found in target-role listings but absent from your selected skills."
              items={analysis.missing_skills}
              tone="missing"
            />
          </div>

          <section className="market-section skill-gap-method">
            <p className="market-eyebrow">How priority works</p>
            <h3>Demand-based, not predictive</h3>
            <p>{analysis.priority_method}</p>
            <p>
              Matching jobs use the existing recommendation matching rule: at least two
              normalized current skills must appear in a target-role listing.
            </p>
          </section>
        </>
      )}
    </section>
  );
}

function Metric({ label, value }) {
  return (
    <article className="market-metric-card">
      <span>{label}</span>
      <strong>{value}</strong>
    </article>
  );
}

function SkillList({ title, subtitle, items, tone }) {
  return (
    <section className="market-section skill-gap-list-section">
      <div className="market-section-heading">
        <div>
          <p className="market-eyebrow">Skill signal</p>
          <h3>{title}</h3>
          <p>{subtitle}</p>
        </div>
      </div>
      {items.length === 0 ? (
        <p className="market-empty">Insufficient data available</p>
      ) : (
        <div className="skill-gap-list">
          {items.slice(0, 15).map((item) => (
            <div className="skill-gap-row" key={item.skill}>
              <div className="skill-gap-row-heading">
                <strong>{item.skill}</strong>
                <span className={`skill-gap-priority ${tone}`}>{item.priority}</span>
              </div>
              <div className="skill-gap-row-meta">
                <span>{item.evidence}</span>
                <strong>{item.percentage}%</strong>
              </div>
              <div className="market-bar-track">
                <div className={`market-bar-fill ${tone}`} style={{ width: `${item.percentage}%` }} />
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}

export default SkillGap;
