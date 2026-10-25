import API_URL from "../config/api.js";
import { useEffect, useState } from "react";


function CompanyIntelligence() {
  const [companyInput, setCompanyInput] = useState("");
  const [suggestions, setSuggestions] = useState([]);
  const [companyData, setCompanyData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const query = companyInput.trim();
    if (query.length < 2) {
      return undefined;
    }

    let cancelled = false;
    fetch(`${API_URL}/companies?query=${encodeURIComponent(query)}`)
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Server returned ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        if (!cancelled) {
          setSuggestions(data.companies || []);
        }
      })
      .catch((requestError) => {
        if (!cancelled) {
          console.error(requestError);
          setSuggestions([]);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [companyInput]);

  const handleCompanyInputChange = (event) => {
    const value = event.target.value;
    setCompanyInput(value);
    if (value.trim().length < 2) {
      setSuggestions([]);
    }
  };

  const analyzeCompany = async (event) => {
    event.preventDefault();
    const company = companyInput.trim();
    setSuggestions([]);
    setError("");
    setCompanyData(null);

    if (!company) {
      setCompanyData({ success: false, message: "Enter a company to explore." });
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(
        `${API_URL}/company-intelligence?company=${encodeURIComponent(company)}`
      );
      if (!response.ok) {
        throw new Error(`Server returned ${response.status}`);
      }
      setCompanyData(await response.json());
    } catch (requestError) {
      console.error(requestError);
      setError(
        "Unable to load Company Intelligence. Make sure FastAPI is running on port 8000."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="company-page">
      <div className="company-hero">
        <div>
          <p className="market-eyebrow">Dataset-derived company evidence</p>
          <h2>Company Intelligence</h2>
          <p>
            Explore the roles, locations, skills, salary records, and
            dataset-listed rating evidence associated with a company.
          </p>
        </div>

        <form className="company-form" onSubmit={analyzeCompany}>
          <label htmlFor="company-search">Search company</label>
          <div className="company-search-row">
            <input
              id="company-search"
              type="search"
              value={companyInput}
              onChange={handleCompanyInputChange}
              placeholder="e.g. Accenture"
              autoComplete="off"
            />
            <button type="submit" disabled={loading}>
              {loading ? "Loading..." : "Analyze Company"}
            </button>
          </div>
          {suggestions.length > 0 && (
            <div className="company-suggestions" role="listbox">
              {suggestions.map((suggestion) => (
                <button
                  key={suggestion.company}
                  type="button"
                  onClick={() => {
                    setCompanyInput(suggestion.company);
                    setSuggestions([]);
                  }}
                >
                  <span>{suggestion.company}</span>
                  <small>{suggestion.job_count.toLocaleString()} jobs</small>
                </button>
              ))}
            </div>
          )}
        </form>
      </div>

      <div className="company-note">
        Company information shown here is derived from the current job-market
        dataset and may not represent the company's complete or current hiring
        activity.
      </div>

      {loading && (
        <div className="market-state" role="status" aria-live="polite">
          <div className="spinner"></div>
          <p>Reading company records from the dataset...</p>
        </div>
      )}

      {error && <div className="error" role="alert">{error}</div>}

      {!loading && companyData && !companyData.success && (
        <div className="market-state">
          <h3>No company data available</h3>
          <p>{companyData.message}</p>
        </div>
      )}

      {!loading && companyData?.success && (
        <>
          <section className="company-section">
            <div className="company-section-heading">
              <div>
                <p className="market-eyebrow">Company overview</p>
                <h3>{companyData.company}</h3>
              </div>
              <span className="market-count">Dataset representation</span>
            </div>
            <div className="company-metrics">
              <Metric label="Jobs represented" value={companyData.job_count} />
              <Metric label="Roles represented" value={companyData.unique_roles} />
              <Metric label="Locations represented" value={companyData.unique_locations} />
              <Metric label="Salary-data jobs" value={companyData.salary_data_jobs} />
            </div>
          </section>

          <div className="company-two-column">
            <CompanyList
              title="Top roles"
              subtitle="Grouped from observed job titles"
              items={companyData.roles}
              valueKey="role"
            />
            <CompanyList
              title="Top locations"
              subtitle="Locations on company job records"
              items={companyData.locations}
              valueKey="location"
            />
          </div>

          <section className="company-section">
            <div className="company-section-heading">
              <div>
                <p className="market-eyebrow">Top skills</p>
                <h3>Skills in company job postings</h3>
              </div>
            </div>
            <div className="company-skill-list">
              {companyData.skills.map((skill) => (
                <div className="company-skill-row" key={skill.skill}>
                  <span>{skill.skill}</span>
                  <div className="company-skill-track">
                    <div
                      className="company-skill-fill"
                      style={{ width: `${skill.demand_percentage}%` }}
                    />
                  </div>
                  <strong>{skill.jobs_with_skill.toLocaleString()}</strong>
                  <small>{skill.demand_percentage}%</small>
                </div>
              ))}
            </div>
          </section>

          <div className="company-two-column">
            <SalarySection salary={companyData.salary} />
            <RatingsSection ratings={companyData.ratings} />
          </div>

          <p className="company-disclaimer">{companyData.message}</p>
        </>
      )}
    </section>
  );
}

function Metric({ label, value }) {
  return (
    <article className="market-metric-card">
      <span>{label}</span>
      <strong>{value.toLocaleString()}</strong>
    </article>
  );
}

function CompanyList({ title, subtitle, items, valueKey }) {
  return (
    <section className="company-section company-list-section">
      <div className="company-section-heading">
        <div>
          <p className="market-eyebrow">Dataset breakdown</p>
          <h3>{title}</h3>
          <p>{subtitle}</p>
        </div>
      </div>
      <div className="company-list">
        {items.map((item) => (
          <div className="company-list-row" key={item[valueKey]}>
            <span>{item[valueKey]}</span>
            <strong>{item.job_count.toLocaleString()}</strong>
          </div>
        ))}
      </div>
    </section>
  );
}

function SalarySection({ salary }) {
  return (
    <section className="company-section">
      <div className="company-section-heading">
        <div>
          <p className="market-eyebrow">Salary intelligence</p>
          <h3>Salary information available in the dataset</h3>
        </div>
      </div>
      {!salary.available ? (
        <p className="company-empty">{salary.message}</p>
      ) : (
        <>
          <div className="company-salary-grid">
            <Metric label="Salary-data jobs" value={salary.salary_jobs} />
            <Metric label="Average" value={`₹${salary.average_salary.toLocaleString("en-IN")}`} />
            <Metric label="Median" value={`₹${salary.median_salary.toLocaleString("en-IN")}`} />
            <Metric label="Minimum" value={`₹${salary.minimum_salary.toLocaleString("en-IN")}`} />
            <Metric label="Maximum" value={`₹${salary.maximum_salary.toLocaleString("en-IN")}`} />
          </div>
          <p className="company-footnote">{salary.message}</p>
        </>
      )}
    </section>
  );
}

function RatingsSection({ ratings }) {
  return (
    <section className="company-section">
      <div className="company-section-heading">
        <div>
          <p className="market-eyebrow">Rating evidence</p>
          <h3>Dataset-listed values</h3>
        </div>
      </div>
      {!ratings.available ? (
        <p className="company-empty">{ratings.message}</p>
      ) : (
        <>
          {ratings.average_dataset_listed_rating !== undefined && (
            <div className="company-rating-value">
              {ratings.average_dataset_listed_rating.toLocaleString()} / 5
            </div>
          )}
          {ratings.average_dataset_listed_review_count !== undefined && (
            <p className="company-footnote">
              Average dataset-listed review count: {ratings.average_dataset_listed_review_count.toLocaleString()}
            </p>
          )}
          <p className="company-footnote">{ratings.message}</p>
        </>
      )}
    </section>
  );
}

export default CompanyIntelligence;
