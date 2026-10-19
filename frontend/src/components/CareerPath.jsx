import { useState } from "react";

const API_URL = "http://127.0.0.1:8000";

function CareerPath() {
  const [roleInput, setRoleInput] = useState("");
  const [pathData, setPathData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const explorePath = async (event) => {
    event.preventDefault();
    setError("");
    setPathData(null);
    setLoading(true);

    try {
      const role = roleInput.trim();
      const response = await fetch(
        `${API_URL}/career-path?role=${encodeURIComponent(role)}`
      );
      if (!response.ok) {
        throw new Error(`Server returned ${response.status}`);
      }

      const data = await response.json();
      setPathData(data);
    } catch (requestError) {
      console.error(requestError);
      setError(
        "Unable to load Career Path. Make sure FastAPI is running on port 8000."
      );
    } finally {
      setLoading(false);
    }
  };

  const hasResults = pathData?.success && pathData.related_roles?.length > 0;

  return (
    <section className="career-path-page">
      <div className="career-path-hero">
        <div>
          <p className="market-eyebrow">Dataset-derived exploration</p>
          <h2>Career Path Explorer</h2>
          <p>
            Explore roles connected by skills and job-title patterns observed
            in the current dataset.
          </p>
        </div>

        <form className="career-path-form" onSubmit={explorePath}>
          <label htmlFor="career-path-role">Starting role</label>
          <div className="career-path-search-row">
            <input
              id="career-path-role"
              type="search"
              value={roleInput}
              onChange={(event) => setRoleInput(event.target.value)}
              placeholder="e.g. Data Analyst"
            />
            <button type="submit" disabled={loading}>
              {loading ? "Exploring..." : "Explore Career Path"}
            </button>
          </div>
        </form>
      </div>

      <div className="career-path-note">
        CareerLens identifies related roles using skills and job-title patterns
        observed in the current dataset. These are dataset-based career
        exploration options, not guaranteed career progression paths.
      </div>

      {loading && (
        <div className="market-state" role="status" aria-live="polite">
          <div className="spinner"></div>
          <p>Comparing observed roles and skills...</p>
        </div>
      )}

      {error && <div className="error" role="alert">{error}</div>}

      {!loading && pathData && !pathData.success && (
        <div className="market-state">
          <h3>Insufficient data available</h3>
          <p>{pathData.message}</p>
        </div>
      )}

      {!loading && hasResults && (
        <>
          <section className="career-path-section">
            <div className="career-path-section-heading">
              <div>
                <p className="market-eyebrow">Current role</p>
                <h3>{pathData.role}</h3>
              </div>
              <span className="market-count">
                {pathData.analyzed_jobs.toLocaleString()} jobs analyzed
              </span>
            </div>
            <div className="career-path-skill-summary">
              <span>Key skills observed in this role</span>
              <div className="career-path-chips">
                {pathData.key_skills.map((skill) => <span key={skill}>{skill}</span>)}
              </div>
            </div>
          </section>

          <section className="career-path-section">
            <div className="career-path-section-heading">
              <div>
                <p className="market-eyebrow">Related career options</p>
                <h3>Observed connections from {pathData.role}</h3>
              </div>
            </div>
            <div className="career-path-flow">
              <div className="career-path-current">{pathData.role}</div>
              <div className="career-path-connector" aria-hidden="true">↓</div>
              <div className="career-path-grid">
                {pathData.related_roles.map((relatedRole) => (
                  <article className="career-path-card" key={relatedRole.role}>
                    <div className="career-path-card-heading">
                      <h4>{relatedRole.role}</h4>
                      <span>{relatedRole.job_count.toLocaleString()} jobs</span>
                    </div>
                    <p className="career-path-overlap">
                      {relatedRole.skill_overlap_percentage}% skill overlap
                    </p>
                    <div className="career-path-detail">
                      <strong>Shared skills</strong>
                      <div className="career-path-chips">
                        {relatedRole.shared_skills.length > 0
                          ? relatedRole.shared_skills.map((skill) => <span key={skill}>{skill}</span>)
                          : <em>None in the selected key skills</em>}
                      </div>
                    </div>
                    <div className="career-path-detail">
                      <strong>Additional observed skills</strong>
                      <div className="career-path-chips muted">
                        {relatedRole.additional_observed_skills.length > 0
                          ? relatedRole.additional_observed_skills.map((skill) => <span key={skill}>{skill}</span>)
                          : <em>None identified</em>}
                      </div>
                    </div>
                    <p className="career-path-evidence">{relatedRole.relationship_evidence}</p>
                  </article>
                ))}
              </div>
            </div>
          </section>
        </>
      )}

      {!loading && pathData?.success && !hasResults && (
        <div className="market-state">
          <h3>No related roles returned</h3>
          <p>{pathData.message}</p>
        </div>
      )}
    </section>
  );
}

export default CareerPath;