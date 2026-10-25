import API_URL from "../config/api.js";
import { useState } from "react";
import { parseSkillInput } from "../utils/skillInput";


function WhatCanIBecome() {
  const [skillsInput, setSkillsInput] = useState("");
  const [matchData, setMatchData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const analyzeSkills = async (event) => {
    event.preventDefault();
    setError("");
    setMatchData(null);
    setLoading(true);

    const skills = parseSkillInput(skillsInput);

    try {
      const response = await fetch(`${API_URL}/what-can-i-become`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ skills }),
      });
      if (!response.ok) {
        throw new Error(`Server returned ${response.status}`);
      }

      setMatchData(await response.json());
    } catch (requestError) {
      console.error(requestError);
      setError(
        "Unable to analyze skills. Make sure FastAPI is running on port 8000."
      );
    } finally {
      setLoading(false);
    }
  };

  const hasRoles = matchData?.success && matchData.roles?.length > 0;

  return (
    <section className="become-page">
      <div className="become-hero">
        <div>
          <p className="market-eyebrow">Dataset-derived skill matching</p>
          <h2>What Can I Become?</h2>
          <p>
            Find roles in the current job dataset whose listings match at
            least two of your selected skills.
          </p>
        </div>

        <form className="become-form" onSubmit={analyzeSkills}>
          <label htmlFor="become-skills">Current skills</label>
          <input
            id="become-skills"
            type="text"
            value={skillsInput}
            onChange={(event) => setSkillsInput(event.target.value)}
            placeholder="Python, SQL, Excel, Power BI"
          />
          <small>Separate skills with commas.</small>
          <button type="submit" disabled={loading}>
            {loading ? "Analyzing..." : "Analyze Skills"}
          </button>
        </form>
      </div>

      <div className="become-note">
        CareerLens searches the current job dataset for roles whose jobs match
        at least two of your selected skills. These results show dataset-based
        skill matches, not guaranteed career outcomes.
      </div>

      {!matchData && !loading && !error && (
        <div className="market-state">
          <h3>Enter at least two skills to explore matching roles.</h3>
        </div>
      )}

      {loading && (
        <div className="market-state" role="status" aria-live="polite">
          <div className="spinner"></div>
          <p>Finding observed role matches...</p>
        </div>
      )}

      {error && <div className="error" role="alert">{error}</div>}

      {!loading && matchData && !matchData.success && (
        <div className="market-state">
          <h3>{matchData.message}</h3>
          {matchData.unrecognized_skills?.length > 0 && (
            <p>
              Unrecognized skills: {matchData.unrecognized_skills.join(", ")}
            </p>
          )}
        </div>
      )}

      {!loading && hasRoles && (
        <>
          <section className="become-section">
            <div className="become-section-heading">
              <div>
                <p className="market-eyebrow">Your skills</p>
                <h3>Recognized selected skills</h3>
              </div>
              <span className="market-count">
                {matchData.skills.length} skills
              </span>
            </div>
            <div className="become-chips">
              {matchData.skills.map((skill) => <span key={skill}>{skill}</span>)}
            </div>
          </section>

          <section className="become-section">
            <div className="become-section-heading">
              <div>
                <p className="market-eyebrow">Dataset overview</p>
                <h3>Observed matching jobs</h3>
              </div>
            </div>
            <div className="become-metrics">
              <article className="market-metric-card">
                <span>Jobs analyzed</span>
                <strong>{matchData.analyzed_jobs.toLocaleString()}</strong>
              </article>
              <article className="market-metric-card">
                <span>Matching jobs</span>
                <strong>{matchData.matching_jobs.toLocaleString()}</strong>
              </article>
            </div>
          </section>

          <section className="become-section">
            <div className="become-section-heading">
              <div>
                <p className="market-eyebrow">Possible role matches</p>
                <h3>Roles with sufficient dataset evidence</h3>
              </div>
            </div>
            <div className="become-role-grid">
              {matchData.roles.map((role) => (
                <article className="become-role-card" key={role.role}>
                  <div className="become-role-heading">
                    <h4>{role.role}</h4>
                    <span>{role.match_percentage}%</span>
                  </div>
                  <div className="become-role-stats">
                    <span>{role.matching_jobs.toLocaleString()} matching jobs</span>
                    <span>{role.role_total_jobs.toLocaleString()} total jobs</span>
                  </div>
                  <div className="become-detail">
                    <strong>Matching skills</strong>
                    <div className="become-chips">
                      {role.matching_skills.map((skill) => <span key={skill}>{skill}</span>)}
                    </div>
                  </div>
                  <div className="become-detail">
                    <strong>Additional common skills</strong>
                    <div className="become-chips muted">
                      {role.missing_common_skills.length > 0
                        ? role.missing_common_skills.map((skill) => <span key={skill}>{skill}</span>)
                        : <em>None identified</em>}
                    </div>
                  </div>
                  <p className="become-evidence">{role.evidence}</p>
                </article>
              ))}
            </div>
          </section>
        </>
      )}

      {!loading && matchData?.success && !hasRoles && (
        <div className="market-state">
          <h3>No roles with sufficient dataset evidence matched your selected skills.</h3>
        </div>
      )}
    </section>
  );
}

export default WhatCanIBecome;
