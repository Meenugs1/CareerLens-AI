import API_URL from "../config/api.js";
import { useState } from "react";
import { parseSkillInput } from "../utils/skillInput";


function CareerSimulator() {
  const [role, setRole] = useState("");
  const [skills, setSkills] = useState("");
  const [addSkill, setAddSkill] = useState("");
  const [simulation, setSimulation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (event) => {
    event.preventDefault();
    const skillList = parseSkillInput(skills);

    if (!role.trim() || skillList.length === 0 || !addSkill.trim()) {
      setSimulation(null);
      setError("Enter a target role, current skills, and a skill to add.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await fetch(`${API_URL}/career-simulator`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          role: role.trim(),
          skills: skillList,
          add_skill: addSkill.trim(),
        }),
      });

      if (!response.ok) {
        throw new Error(`Server returned ${response.status}`);
      }

      const data = await response.json();
      setSimulation(data);
      if (
        !data.success &&
        !(data.summary?.target_role_jobs > 0 && data.before && data.after)
      ) {
        setError(data.message || "The selected simulation could not be calculated.");
      }
    } catch (requestError) {
      console.error(requestError);
      setSimulation(null);
      setError(
        "Unable to load Career Simulator. Make sure FastAPI is running on port 8000."
      );
    } finally {
      setLoading(false);
    }
  };

  const hasComparison =
    simulation?.summary?.target_role_jobs > 0 &&
    simulation.before &&
    simulation.after;

  return (
    <section className="simulator-page">
      <div className="simulator-hero">
        <div>
          <p className="market-eyebrow">Dataset-based what-if analysis</p>
          <h2>Career Simulator</h2>
          <p>
            See how one additional skill changes matches within the analyzed
            jobs for your target role. It does not guarantee employment.
          </p>
        </div>

        <form className="simulator-form" onSubmit={handleSubmit}>
          <label htmlFor="simulator-role">Target role</label>
          <input
            id="simulator-role"
            value={role}
            onChange={(event) => setRole(event.target.value)}
            placeholder="e.g. Data Analyst"
          />
          <label htmlFor="simulator-skills">Current skills</label>
          <input
            id="simulator-skills"
            value={skills}
            onChange={(event) => setSkills(event.target.value)}
            placeholder="Python, SQL"
          />
          <label htmlFor="simulator-add-skill">Skill to add</label>
          <input
            id="simulator-add-skill"
            value={addSkill}
            onChange={(event) => setAddSkill(event.target.value)}
            placeholder="Power BI"
          />
          <button type="submit" disabled={loading}>
            {loading ? "Simulating..." : "Run What-If"}
          </button>
        </form>
      </div>

      <p className="simulator-explanation">
        CareerLens compares your selected skills against jobs for this role in
        the current dataset. Results are dataset-based and do not guarantee employment.
      </p>

      {loading && (
        <div className="market-state" role="status" aria-live="polite">
          <div className="spinner"></div>
          <p>Recalculating role matches...</p>
        </div>
      )}

      {error && !loading && (
        <div className="error" role="alert">
          {error}
        </div>
      )}

      {!loading && hasComparison && (
        <SimulationResults data={simulation} addedSkill={addSkill.trim()} />
      )}

      {!loading && simulation && !hasComparison && (
        <div className="market-state">
          <h3>{simulation.message || "Insufficient data available"}</h3>
          <p>The simulator did not report an improvement for this input.</p>
        </div>
      )}
    </section>
  );
}

function SimulationResults({ data, addedSkill }) {
  return (
    <>
      <section className="market-section simulator-overview">
        <div className="market-section-heading">
          <div>
            <p className="market-eyebrow">Comparison</p>
            <h3>{data.role}</h3>
          </div>
          <span className="market-count">
            {data.summary.target_role_jobs.toLocaleString()} analyzed jobs
          </span>
        </div>
        <div className="simulator-comparison-grid">
          <ComparisonCard title="Before" skills={data.before.skills} matching={data.before.matching_jobs} coverage={data.before.coverage} />
          <div className="simulator-arrow" aria-hidden="true">→</div>
          <ComparisonCard title="After adding skill" skills={data.after.skills} matching={data.after.matching_jobs} coverage={data.after.coverage} highlighted />
        </div>
      </section>

      <section className="market-section simulator-impact">
        <div className="market-section-heading">
          <div>
            <p className="market-eyebrow">Impact</p>
            <h3>What changed in the dataset</h3>
          </div>
          <span className="simulator-added-skill">
            + {data.after.added_skill || addedSkill}
          </span>
        </div>
        <div className="market-metric-grid simulator-impact-grid">
          <Metric label="Matching jobs change" value={formatChange(data.impact.matching_jobs_change, "jobs")} />
          <Metric label="Coverage change" value={formatChange(data.impact.coverage_change, "percentage points")} />
        </div>
        <p className="simulator-note">{data.message}</p>
        <p className="simulator-note">{data.coverage_definition}</p>
      </section>
    </>
  );
}

function ComparisonCard({ title, skills, matching, coverage, highlighted }) {
  return (
    <article className={`simulator-comparison-card ${highlighted ? "highlighted" : ""}`}>
      <p className="market-eyebrow">{title}</p>
      <div className="simulator-value-row">
        <strong>{matching.toLocaleString()}</strong>
        <span>matching jobs</span>
      </div>
      <div className="simulator-coverage">{coverage}% coverage</div>
      <div className="simulator-skill-chips">
        {skills.map((skill) => <span key={skill}>{skill}</span>)}
      </div>
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

function formatChange(value, unit) {
  const sign = value > 0 ? "+" : "";
  return `${sign}${value} ${unit}`;
}

export default CareerSimulator;
