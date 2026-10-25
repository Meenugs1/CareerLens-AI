import API_URL from "../config/api.js";
import { useState } from "react";
import { parseSkillInput } from "../utils/skillInput";


function CareerSwitch() {
  const [currentRole, setCurrentRole] = useState("");
  const [currentSkills, setCurrentSkills] = useState("");
  const [targetRole, setTargetRole] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (event) => {
    event.preventDefault();
    const skills = parseSkillInput(currentSkills);

    if (!currentRole.trim() || !targetRole.trim() || skills.length === 0) {
      setAnalysis(null);
      setError("Enter your current role, current skills, and a target role.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await fetch(`${API_URL}/career-switch`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          current_role: currentRole.trim(),
          current_skills: skills,
          target_role: targetRole.trim(),
        }),
      });

      if (!response.ok) {
        throw new Error(`Server returned ${response.status}`);
      }

      const data = await response.json();
      setAnalysis(data);
      if (!data.success) {
        setError(data.message || "The switch analysis could not be calculated.");
      }
    } catch (requestError) {
      console.error(requestError);
      setAnalysis(null);
      setError(
        "Unable to load Career Switch Analysis. Make sure FastAPI is running on port 8000."
      );
    } finally {
      setLoading(false);
    }
  };

  const hasTargetData = analysis?.success && analysis.target_role?.analyzed_jobs > 0;

  return (
    <section className="career-switch-page">
      <div className="career-switch-hero">
        <div>
          <p className="market-eyebrow">Dataset-derived transition view</p>
          <h2>Career Switch Analyzer</h2>
          <p>
            Compare your current skills with skills observed in jobs for a
            selected target role. This describes dataset relationships, not career outcomes.
          </p>
        </div>

        <form className="career-switch-form" onSubmit={handleSubmit}>
          <label htmlFor="switch-current-role">Current role</label>
          <input
            id="switch-current-role"
            value={currentRole}
            onChange={(event) => setCurrentRole(event.target.value)}
            placeholder="e.g. Data Analyst"
          />
          <label htmlFor="switch-current-skills">Current skills</label>
          <input
            id="switch-current-skills"
            value={currentSkills}
            onChange={(event) => setCurrentSkills(event.target.value)}
            placeholder="Python, SQL, Excel, Power BI"
          />
          <label htmlFor="switch-target-role">Target role</label>
          <input
            id="switch-target-role"
            value={targetRole}
            onChange={(event) => setTargetRole(event.target.value)}
            placeholder="e.g. Frontend Developer"
          />
          <button type="submit" disabled={loading}>
            {loading ? "Comparing..." : "Analyze Career Switch"}
          </button>
        </form>
      </div>

      <p className="career-switch-explanation">
        CareerLens compares your current skills with skills observed in jobs for
        the selected target role. Results are based on the current dataset and
        do not guarantee employment or career outcomes.
      </p>

      {loading && (
        <div className="market-state" role="status" aria-live="polite">
          <div className="spinner"></div>
          <p>Comparing target-role evidence...</p>
        </div>
      )}

      {error && !loading && (
        <div className="error" role="alert">
          {error}
        </div>
      )}

      {!loading && analysis && !analysis.success && (
        <div className="market-state">
          <h3>{analysis.message || "Insufficient data available"}</h3>
          <p>Select a different target role or provide more complete profile information.</p>
        </div>
      )}

      {!loading && hasTargetData && <CareerSwitchResults data={analysis} />}
    </section>
  );
}

function CareerSwitchResults({ data }) {
  const overlap = data.skill_overlap.overlap_skills;
  const missing = data.skill_overlap.missing_skills;

  return (
    <>
      <div className="career-switch-flow">
        <FlowCard title="Current profile" value={data.current_profile.role} detail={`${data.current_profile.skills.length} normalized skills`} />
        <span aria-hidden="true">↓</span>
        <FlowCard title="Skill overlap" value={`${data.switch_gap.overlap_count} of 10`} detail="common target-role skills" />
        <span aria-hidden="true">↓</span>
        <FlowCard title="Target role" value={data.target_role.role} detail={`${data.target_role.analyzed_jobs.toLocaleString()} analyzed jobs`} highlighted />
      </div>

      <section className="market-section career-switch-section">
        <div className="market-section-heading">
          <div>
            <p className="market-eyebrow">Current profile</p>
            <h3>{data.current_profile.role}</h3>
          </div>
          <span className="market-count">{data.current_profile.skills.length} skills</span>
        </div>
        <div className="career-switch-chips">
          {data.current_profile.skills.map((skill) => <span key={skill}>{skill}</span>)}
        </div>
      </section>

      <div className="career-switch-columns">
        <SkillEvidence title="Skill overlap" subtitle="Current skills in the target role's top 10 observed skills." items={overlap} tone="overlap" />
        <SkillEvidence title="Missing target skills" subtitle={data.skill_overlap.skill_set_definition} items={missing} tone="missing" />
      </div>

      <section className="market-section career-switch-section">
        <div className="market-section-heading">
          <div>
            <p className="market-eyebrow">Switch gap</p>
            <h3>{data.target_role.role}</h3>
            <p>Matching uses the existing rule: at least two normalized current skills in a target-role job.</p>
          </div>
          <span className="market-count">{data.switch_gap.target_role_jobs.toLocaleString()} analyzed jobs</span>
        </div>
        <div className="market-metric-grid career-switch-metrics">
          <Metric label="Matching target jobs" value={data.switch_gap.matching_jobs.toLocaleString()} />
          <Metric label="Target-role coverage" value={`${data.switch_gap.coverage}%`} />
          <Metric label="Overlap skills" value={data.switch_gap.overlap_count} />
          <Metric label="Key missing skills" value={data.switch_gap.missing_count} />
        </div>
      </section>

      <section className="market-section career-switch-section">
        <p className="market-eyebrow">Transition summary</p>
        <h3>Observed skill relationship</h3>
        <p className="career-switch-summary">{data.readiness_summary}</p>
        <p className="career-switch-note">{data.message}</p>
      </section>
    </>
  );
}

function SkillEvidence({ title, subtitle, items, tone }) {
  return (
    <section className="market-section career-switch-section">
      <div className="market-section-heading">
        <div>
          <p className="market-eyebrow">Target-role evidence</p>
          <h3>{title}</h3>
          <p>{subtitle}</p>
        </div>
      </div>
      {items.length === 0 ? (
        <p className="market-empty">No overlap found in the selected common skill set.</p>
      ) : (
        <div className="career-switch-skill-list">
          {items.map((item) => (
            <div className="career-switch-skill" key={item.skill}>
              <div>
                <strong>{item.skill}</strong>
                <span>{item.evidence}</span>
              </div>
              <div className={`career-switch-badge ${tone}`}>{item.priority}</div>
              <b>{item.demand_percentage}%</b>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}

function FlowCard({ title, value, detail, highlighted }) {
  return (
    <article className={`career-switch-flow-card ${highlighted ? "highlighted" : ""}`}>
      <p className="market-eyebrow">{title}</p>
      <strong>{value}</strong>
      <span>{detail}</span>
    </article>
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

export default CareerSwitch;
