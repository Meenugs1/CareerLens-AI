import API_URL from "./config/api.js";
import { useState } from "react";
import "./App.css";
import Header from "./components/Header";
import JobCard from "./components/JobCard";
import CareerSimulator from "./components/CareerSimulator";
import CareerSwitch from "./components/CareerSwitch";
import CareerPath from "./components/CareerPath";
import WhatCanIBecome from "./components/WhatCanIBecome";
import CompanyIntelligence from "./components/CompanyIntelligence";
import MarketIntelligence from "./components/MarketIntelligence";
import SearchForm from "./components/SearchForm";
import SkillGap from "./components/SkillGap";
import SummaryCards from "./components/SummaryCards";


function App() {
  const [results, setResults] = useState([]);
  const [summary, setSummary] = useState(null);
  const [otherRelevantInternships, setOtherRelevantInternships] = useState([]);
  const [limitedSkillOverlapInternships, setLimitedSkillOverlapInternships] = useState([]);
  const [internshipCoverage, setInternshipCoverage] = useState(null);
  const [submittedJobType, setSubmittedJobType] = useState("Any");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [formVersion, setFormVersion] = useState(0);
  const [activeView, setActiveView] = useState("home");

  const handleRecommend = async (request) => {
    setError("");
    setResults([]);
    setSummary(null);
    setOtherRelevantInternships([]);
    setLimitedSkillOverlapInternships([]);
    setInternshipCoverage(null);
    setSubmittedJobType(request.job_type);
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/recommend`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          role: request.role,
          skills: request.skills,
          experience: request.experience,
          location: request.location,
          work_mode: request.work_mode,
          job_type: request.job_type,
        }),
      });

      if (!response.ok) {
        throw new Error(`Server returned ${response.status}`);
      }

      const data = await response.json();

      if (!data.success) {
        throw new Error("Recommendation request failed.");
      }

      const recommendationData = data.results || {};
      setResults(Array.isArray(recommendationData.recommendations)
        ? recommendationData.recommendations
        : []);
      setSummary(recommendationData.summary || null);
      setOtherRelevantInternships(
        Array.isArray(recommendationData.other_relevant_internships)
          ? recommendationData.other_relevant_internships
          : []
      );
      setLimitedSkillOverlapInternships(
        Array.isArray(recommendationData.limited_skill_overlap_internships)
          ? recommendationData.limited_skill_overlap_internships
          : []
      );
      setInternshipCoverage(recommendationData.internship_coverage || null);
    } catch (requestError) {
      console.error(requestError);
      setError(
        "Unable to connect to the CareerLens AI backend. Make sure FastAPI is running on port 8000."
      );
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormVersion((version) => version + 1);
    setResults([]);
    setSummary(null);
    setOtherRelevantInternships([]);
    setLimitedSkillOverlapInternships([]);
    setInternshipCoverage(null);
    setSubmittedJobType("Any");
    setError("");
  };

  return (
    <div className="app min-h-screen bg-slate-950">
      <Header activeView={activeView} onNavigate={setActiveView} />

      <main className="container">
        {activeView === "market" ? (
          <MarketIntelligence />
        ) : activeView === "skill-gap" ? (
          <SkillGap />
        ) : activeView === "simulator" ? (
          <CareerSimulator />
        ) : activeView === "switch" ? (
          <CareerSwitch />
        ) : activeView === "career-path" ? (
          <CareerPath />
        ) : activeView === "what-can-i-become" ? (
          <WhatCanIBecome />
        ) : activeView === "company-intelligence" ? (
          <CompanyIntelligence />
        ) : (
          <>
            <SearchForm
              key={formVersion}
              onSearch={handleRecommend}
              onReset={resetForm}
              loading={loading}
            />

            {error && (
              <div className="error" role="alert">
                {error}
              </div>
            )}

            {loading && (
              <div className="loading" role="status" aria-live="polite">
                <div className="spinner"></div>
                <p>Analyzing jobs and calculating matches...</p>
              </div>
            )}

            {!loading && summary && <SummaryCards summary={summary} />}

            {!loading && submittedJobType === "Internship" && internshipCoverage && (
              <section className="internship-fallback" aria-labelledby="internship-coverage-title">
                <div className="internship-fallback-heading">
                  <h2 id="internship-coverage-title">Internship data coverage</h2>
                  <span>{internshipCoverage.displayed_listings} of up to 7 shown</span>
                </div>
                <p>
                  {internshipCoverage.coverage_limited
                    ? `Limited dataset coverage: ${internshipCoverage.coverage_message} All verified relevant listings are shown; results are not padded.`
                    : `${internshipCoverage.verified_internship_listings} verified role-relevant internship listings were found in the dataset.`}
                </p>
                <p>
                  Skills are explicitly supplied for {internshipCoverage.listings_with_explicit_skills} listings;
                  {" "}{internshipCoverage.listings_with_text_extracted_skills} listings have skills extracted from title or description text.
                  {" "}{internshipCoverage.standard_skill_matches} meet the standard skill-match threshold.
                </p>
              </section>
            )}

            {!loading && results.length > 0 && (
              <section className="results-section">
                <div className="results-header">
                  <div>
                    <h2>Recommended Jobs</h2>
                    <p>
                      Showing the best matching opportunities based on your
                      preferences.
                    </p>
                  </div>

                  <span className="result-count">{results.length} jobs</span>
                </div>

                <div className="jobs-list">
                  {results.map((job, index) => (
                    <JobCard key={job.job_id || index} job={job} rank={index + 1} />
                  ))}
                </div>
              </section>
            )}

            {!loading && limitedSkillOverlapInternships.length > 0 && (
              <section className="internship-fallback" aria-labelledby="internship-limited-title">
                <div className="internship-fallback-heading">
                  <h2 id="internship-limited-title">Limited skill overlap</h2>
                  <span>{limitedSkillOverlapInternships.length} listings</span>
                </div>
                <p>
                  These verified, role-relevant internships overlap with exactly
                  one selected skill. This is a weaker match than the standard
                  recommendations above.
                </p>
                <div className="internship-fallback-list">
                  {limitedSkillOverlapInternships.map((job, index) => (
                    <article
                      key={job.job_id || `${job.job_title}-${index}`}
                      className="internship-fallback-item"
                    >
                      <div>
                        <h3>{job.job_title}</h3>
                        <p>{job.company || "Company not specified"}</p>
                        <span>{job.location || "Location not specified"}</span>
                      </div>
                      <div className="internship-fallback-status">
                        <strong>Limited skill overlap</strong>
                        <span>
                          {job.matched_skill_evidence
                            ?.map((item) => `${item.skill} (${item.sources.join(" and ")})`)
                            .join(", ") || job.matched_skills.join(", ")}
                        </span>
                        {job.role_evidence && <span>{job.role_evidence}</span>}
                      </div>
                    </article>
                  ))}
                </div>
              </section>
            )}

            {!loading && otherRelevantInternships.length > 0 && (
              <section className="internship-fallback" aria-labelledby="internship-fallback-title">
                <div className="internship-fallback-heading">
                  <h2 id="internship-fallback-title">Skill data incomplete</h2>
                  <span>{otherRelevantInternships.length} listings</span>
                </div>
                <p>
                  These verified, role-relevant internships have fewer than two
                  normalized dataset skills. A reliable skills match cannot be
                  calculated, so they are not scored or included above.
                </p>
                <div className="internship-fallback-list">
                  {otherRelevantInternships.map((job) => (
                    <article key={job.job_id} className="internship-fallback-item">
                      <div>
                        <h3>{job.job_title}</h3>
                        <p>{job.company || "Company not specified"}</p>
                        <span>{job.location || "Location not specified"}</span>
                      </div>
                      <div className="internship-fallback-status">
                        <strong>Verified internship</strong>
                        <span>{job.match_status}</span>
                        {job.skill_evidence?.some((item) => item.sources.includes("description")) && (
                          <span>
                            Skills extracted from the listing description: {job.skill_evidence
                              .filter((item) => item.sources.includes("description"))
                              .map((item) => item.skill)
                              .join(", ")}
                          </span>
                        )}
                      </div>
                    </article>
                  ))}
                </div>
              </section>
            )}

            {!loading && summary && (
              (submittedJobType === "Internship" && (summary.jobs_analyzed === 0 || results.length === 0)) ||
              (results.length === 0 && otherRelevantInternships.length === 0 && limitedSkillOverlapInternships.length === 0)
            ) && (
              <div className="no-results">
                <h2>
                  {submittedJobType === "Internship" && summary.jobs_analyzed === 0
                    ? "No role-relevant internship listings were found for this role."
                    : submittedJobType === "Internship"
                      ? "No internship listings met the standard two-skill match criteria."
                    : "No matching jobs found for your selected criteria."}
                </h2>
                <p>
                  {submittedJobType === "Internship" && summary.jobs_analyzed > 0
                    ? `${summary.jobs_analyzed} role-relevant internship listings were analyzed. The standard recommendations require at least two overlapping skills; weaker or incomplete matches, when available, are listed below.`
                    : "Try changing your skills, location, job type, or target role."}
                </p>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}

export default App;
