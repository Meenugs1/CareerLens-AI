import { useEffect, useRef, useState } from "react";

const API_URL = "http://127.0.0.1:8000";

const overviewCards = [
  ["Total Jobs", "total_jobs"],
  ["Jobs With Salary", "jobs_with_salary"],
  ["Unique Companies", "unique_companies"],
  ["Unique Locations", "unique_locations"],
  ["Unique Job Titles", "unique_job_titles"],
];

function displayNumber(value) {
  return typeof value === "number" ? value.toLocaleString() : "Insufficient data available";
}

function displaySalary(value) {
  if (typeof value !== "number") {
    return "Insufficient data available";
  }

  return `₹${value.toLocaleString("en-IN", { maximumFractionDigits: 2 })}`;
}

function MarketIntelligence() {
  const [roleInput, setRoleInput] = useState("");
  const [activeRole, setActiveRole] = useState("");
  const [marketData, setMarketData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const requestCache = useRef(new Map());

  const fetchMarketData = async (role) => {
    const normalizedRole = role.trim();
    const cachedData = requestCache.current.get(normalizedRole);

    setActiveRole(normalizedRole);
    setError("");

    if (cachedData) {
      setMarketData(cachedData);
      setLoading(false);
      return;
    }

    setLoading(true);

    try {
      const query = normalizedRole
        ? `?role=${encodeURIComponent(normalizedRole)}`
        : "";
      const response = await fetch(`${API_URL}/market-intelligence${query}`);

      if (!response.ok) {
        throw new Error(`Server returned ${response.status}`);
      }

      const data = await response.json();
      if (!data.success) {
        throw new Error("Market Intelligence request failed.");
      }

      requestCache.current.set(normalizedRole, data);
      setMarketData(data);
    } catch (requestError) {
      console.error(requestError);
      setMarketData(null);
      setError(
        "Unable to load Market Intelligence. Make sure FastAPI is running on port 8000."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    Promise.resolve().then(() => fetchMarketData(""));
  }, []);

  const handleSubmit = (event) => {
    event.preventDefault();
    fetchMarketData(roleInput);
  };

  const overview = marketData?.overview;
  const salary = marketData?.salary_intelligence;
  const hasData = Boolean(marketData && overview && overview.total_jobs > 0);

  return (
    <section className="market-page">
      <div className="market-hero">
        <div>
          <p className="market-eyebrow">Dataset-derived insights</p>
          <h2>Job Market Intelligence</h2>
          <p>
            Explore what the current job market is asking for across roles,
            locations, companies, skills, experience, and salary ranges.
          </p>
        </div>

        <form className="market-role-search" onSubmit={handleSubmit}>
          <label htmlFor="market-role">Focus on a role</label>
          <div className="market-search-row">
            <input
              id="market-role"
              type="search"
              value={roleInput}
              onChange={(event) => setRoleInput(event.target.value)}
              placeholder="e.g. Data Analyst"
            />
            <button type="submit" disabled={loading}>
              {loading ? "Loading..." : "Explore"}
            </button>
          </div>
          {activeRole && (
            <button
              className="market-clear-button"
              type="button"
              onClick={() => {
                setRoleInput("");
                fetchMarketData("");
              }}
            >
              Showing: {activeRole} · Clear role
            </button>
          )}
        </form>
      </div>

      {loading && (
        <div className="market-state" role="status" aria-live="polite">
          <div className="spinner"></div>
          <p>Reading the current job market...</p>
        </div>
      )}

      {error && (
        <div className="error" role="alert">
          {error}
        </div>
      )}

      {!loading && marketData && !hasData && (
        <div className="market-state">
          <h3>Insufficient data available</h3>
          <p>No market records matched this role.</p>
        </div>
      )}

      {!loading && hasData && (
        <>
          <div className="market-disclaimer">
            Figures are calculated from the current cleaned job dataset. They describe observed listings and do not guarantee salary or hiring outcomes.
          </div>

          <section className="market-section">
            <div className="market-section-heading">
              <div>
                <p className="market-eyebrow">Market overview</p>
                <h3>{activeRole || "The full job market"}</h3>
              </div>
              <span className="market-count">{displayNumber(overview.total_jobs)} listings</span>
            </div>
            <div className="market-metric-grid">
              {overviewCards.map(([label, key]) => (
                <article className="market-metric-card" key={key}>
                  <span>{label}</span>
                  <strong>{displayNumber(overview[key])}</strong>
                </article>
              ))}
            </div>
          </section>

          <div className="market-two-column">
            <MarketList
              title="Top locations"
              subtitle="Where listings are concentrated"
              items={marketData.top_locations}
              valueKey="location"
              valueLabel="location"
              showPercentage
            />
            <MarketList
              title="Top companies"
              subtitle="Employers with the most listings"
              items={marketData.top_companies}
              valueKey="company"
              valueLabel="company"
            />
          </div>

          <div className="market-two-column">
            <MarketList
              title="Most demanded skills"
              subtitle="Skills appearing in the dataset tags"
              items={marketData.top_skills}
              valueKey="skill"
              valueLabel="skill"
              showPercentage
            />
            <MarketList
              title="Experience distribution"
              subtitle="Based on the cleaned minimum experience field"
              items={marketData.experience_distribution}
              valueKey="experience_group"
              valueLabel="experience group"
              showPercentage
            />
          </div>

          <section className="market-section">
            <div className="market-section-heading">
              <div>
                <p className="market-eyebrow">Salary intelligence</p>
                <h3>Observed salary data</h3>
              </div>
              <span className="market-count">INR listings only</span>
            </div>
            <div className="market-salary-grid">
              {[
                ["Average Salary", salary.average_salary],
                ["Median Salary", salary.median_salary],
                ["Minimum Salary", salary.minimum_salary],
                ["Maximum Salary", salary.maximum_salary],
                ["Salary Job Count", salary.salary_job_count],
              ].map(([label, value]) => (
                <article className="market-metric-card" key={label}>
                  <span>{label}</span>
                  <strong>{label === "Salary Job Count" ? displayNumber(value) : displaySalary(value)}</strong>
                </article>
              ))}
            </div>
            {salary.salary_range_distribution?.length > 0 && (
              <div className="market-range-list">
                {salary.salary_range_distribution.map((range) => (
                  <div className="market-range-row" key={range.salary_range}>
                    <span>{range.salary_range}</span>
                    <div className="market-bar-track">
                      <div className="market-bar-fill" style={{ width: `${range.percentage_of_salary_jobs}%` }} />
                    </div>
                    <strong>{range.job_count.toLocaleString()}</strong>
                  </div>
                ))}
              </div>
            )}
          </section>

          <div className="market-two-column">
            <MarketList
              title="Top roles"
              subtitle="Most frequent job titles"
              items={marketData.top_roles}
              valueKey="job_title"
              valueLabel="job title"
            />
            <MarketList
              title="Related roles"
              subtitle={activeRole ? `Titles related to ${activeRole}` : "Search a role to see related titles"}
              items={marketData.related_roles}
              valueKey="job_title"
              valueLabel="job title"
            />
          </div>
        </>
      )}
    </section>
  );
}

function MarketList({ title, subtitle, items = [], valueKey, valueLabel, showPercentage }) {
  return (
    <section className="market-section market-list-section">
      <div className="market-section-heading">
        <div>
          <p className="market-eyebrow">Market signal</p>
          <h3>{title}</h3>
          <p>{subtitle}</p>
        </div>
      </div>
      {items.length === 0 ? (
        <p className="market-empty">Insufficient data available</p>
      ) : (
        <div className="market-list">
          {items.map((item, index) => (
            <div className="market-list-row" key={`${item[valueKey]}-${index}`}>
              <div className="market-list-label">
                <span className="market-rank">{String(index + 1).padStart(2, "0")}</span>
                <strong title={item[valueKey]}>{item[valueKey]}</strong>
              </div>
              <div className="market-list-value">
                <div className="market-bar-track">
                  <div
                    className="market-bar-fill"
                    style={{ width: `${showPercentage ? item.percentage_of_jobs : Math.min(100, (item.job_count / (items[0].job_count || 1)) * 100)}%` }}
                  />
                </div>
                <span>{item.job_count.toLocaleString()}</span>
                {showPercentage && <small>{item.percentage_of_jobs}%</small>}
              </div>
            </div>
          ))}
        </div>
      )}
      <span className="market-list-caption">{valueLabel} count across observed listings</span>
    </section>
  );
}

export default MarketIntelligence;
