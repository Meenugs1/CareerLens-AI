function JobCard({ job, rank }) {
  // ------------------------------------------------------------
  // SAFE VALUE CONVERSION
  // ------------------------------------------------------------
  const toNumber = (value, fallback = 0) => {
    const number = Number(value)

    return Number.isFinite(number) ? number : fallback
  }

  const score = toNumber(job?.recommendation_score)

  const skillMatch = toNumber(job?.skill_match)
  const roleRelevance = toNumber(job?.role_relevance)
  const experienceMatch = toNumber(job?.experience_match)
  const locationMatch = toNumber(job?.location_match)
  const workModeMatch = toNumber(job?.work_mode_match)
  const freshnessScore = toNumber(job?.freshness_score)

  // ------------------------------------------------------------
  // SCORE COLOR
  // ------------------------------------------------------------
  const getScoreClass = () => {
    if (score >= 75) {
      return "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
    }

    if (score >= 60) {
      return "bg-blue-500/10 text-blue-400 border-blue-500/20"
    }

    if (score >= 45) {
      return "bg-amber-500/10 text-amber-400 border-amber-500/20"
    }

    return "bg-red-500/10 text-red-400 border-red-500/20"
  }

  // ------------------------------------------------------------
  // LOCATION COLOR
  // ------------------------------------------------------------
  const getLocationClass = () => {
    if (locationMatch >= 100) {
      return "bg-emerald-500/10 text-emerald-400"
    }

    if (locationMatch >= 70) {
      return "bg-blue-500/10 text-blue-400"
    }

    if (locationMatch >= 30) {
      return "bg-amber-500/10 text-amber-400"
    }

    return "bg-red-500/10 text-red-400"
  }

  // ------------------------------------------------------------
  // LOCATION STATUS TEXT
  // ------------------------------------------------------------
  const getLocationStatus = () => {
    if (locationMatch >= 100) {
      return "✓ Preferred Location"
    }

    if (locationMatch >= 70) {
      return "≈ Nearby Location"
    }

    if (locationMatch >= 30) {
      return "△ Same State"
    }

    return "✕ Different Location"
  }

  // ------------------------------------------------------------
  // WORK MODE
  // ------------------------------------------------------------
  const workMode = job?.work_mode || "Not Specified"

  // ------------------------------------------------------------
  // RENDER
  // ------------------------------------------------------------
  return (
    <article className="rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-lg transition hover:border-slate-700">

      {/* ======================================================
          HEADER
      ====================================================== */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">

        {/* Job information */}
        <div className="min-w-0">

          {/* Rank + Job Title */}
          <div className="mb-2 flex items-start gap-3">

            <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-slate-800 text-sm font-bold text-slate-300">
              {rank}
            </span>

            <h3 className="text-lg font-semibold text-white">
              {job?.job_title || "Job Title Not Available"}
            </h3>

          </div>

          {/* Company */}
          <p className="text-sm font-medium text-blue-400">
            {job?.company || "Company Not Available"}
          </p>

          {/* Location + Work Mode */}
          <div className="mt-2 flex flex-wrap items-center gap-2 text-sm text-slate-400">

            <span>
              📍 {job?.location || "Location Not Specified"}
            </span>

            {workMode &&
              workMode.toLowerCase() !== "unknown" &&
              workMode.toLowerCase() !== "not specified" && (
                <span>
                  • {workMode}
                </span>
              )}

          </div>

        </div>

        {/* Recommendation Score */}
        <div
          className={`shrink-0 rounded-xl border px-4 py-3 text-center ${getScoreClass()}`}
        >
          <p className="text-2xl font-bold">
            {score.toFixed(1)}%
          </p>

          <p className="text-xs">
            Recommendation Score
          </p>
        </div>

      </div>


      {/* ======================================================
          MATCH LEVEL
      ====================================================== */}
      <div className="mt-5 flex flex-wrap gap-2">

        <span className="rounded-full bg-slate-800 px-3 py-1 text-xs font-semibold text-slate-300">
          {job?.match_level || "Match"}
        </span>

        {job?.fresher_suitable === "Yes" && (
          <span className="rounded-full bg-emerald-500/10 px-3 py-1 text-xs font-semibold text-emerald-400">
            ✓ Fresher Suitable
          </span>
        )}

        {job?.fresher_suitable === "No" && (
          <span className="rounded-full bg-red-500/10 px-3 py-1 text-xs font-semibold text-red-400">
            ✕ Not Fresher Suitable
          </span>
        )}

      </div>


      {/* ======================================================
          SALARY
      ====================================================== */}
      {job?.salary_range &&
        job.salary_range !== "nan" &&
        job.salary_range !== "None" &&
        job.salary_range !== "null" && (

          <div className="mt-5 rounded-xl bg-slate-950 p-4">

            <p className="text-xs text-slate-500">
              Salary
            </p>

            <p className="mt-1 font-semibold text-emerald-400">
              {job.salary_range}
            </p>

          </div>
        )}


      {/* ======================================================
          LOCATION STATUS
      ====================================================== */}
      <div className="mt-5 rounded-xl bg-slate-950 p-4">

        <div className="flex items-center justify-between gap-3">

          <div>

            <p className="text-xs text-slate-500">
              Location Status
            </p>

            <p
              className={`mt-2 inline-flex rounded-full px-3 py-1 text-xs font-semibold ${getLocationClass()}`}
            >
              {getLocationStatus()}
            </p>

          </div>

          <div className="text-right">

            <p className="text-xs text-slate-500">
              Location Match
            </p>

            <p className={`mt-1 text-xl font-bold ${getLocationClass().split(" ")[1]}`}>
              {locationMatch.toFixed(0)}%
            </p>

          </div>

        </div>

      </div>


      {/* ======================================================
          MATCH STATISTICS
      ====================================================== */}
      <div className="mt-6 grid grid-cols-2 gap-4 md:grid-cols-4">

        {/* Skill Match */}
        <div className="rounded-xl bg-slate-950 p-4">

          <p className="text-xs text-slate-500">
            Skill Match
          </p>

          <p className="mt-1 font-semibold text-white">
            {skillMatch.toFixed(1)}%
          </p>

        </div>


        {/* Role Relevance */}
        <div className="rounded-xl bg-slate-950 p-4">

          <p className="text-xs text-slate-500">
            Role Relevance
          </p>

          <p className="mt-1 font-semibold text-white">
            {roleRelevance.toFixed(0)}%
          </p>

        </div>


        {/* Experience Match */}
        <div className="rounded-xl bg-slate-950 p-4">

          <p className="text-xs text-slate-500">
            Experience Match
          </p>

          <p className="mt-1 font-semibold text-white">
            {experienceMatch.toFixed(1)}%
          </p>

        </div>


        {/* Work Mode Match */}
        <div className="rounded-xl bg-slate-950 p-4">

          <p className="text-xs text-slate-500">
            Work Mode Match
          </p>

          <p className="mt-1 font-semibold text-white">
            {workModeMatch.toFixed(0)}%
          </p>

        </div>

      </div>


      {/* ======================================================
          FRESHNESS
      ====================================================== */}
      <div className="mt-4 rounded-xl bg-slate-950 p-4">

        <div className="flex items-center justify-between">

          <div>

            <p className="text-xs text-slate-500">
              Job Freshness
            </p>

            <p className="mt-1 font-semibold text-white">
              {freshnessScore.toFixed(0)}%
            </p>

          </div>

          <div className="text-right">

            <p className="text-xs text-slate-500">
              Job ID
            </p>

            <p className="mt-1 max-w-[180px] truncate text-xs text-slate-400">
              {job?.job_id || "Not Available"}
            </p>

          </div>

        </div>

      </div>


      {/* ======================================================
          MATCHED SKILLS
      ====================================================== */}
      {Array.isArray(job?.matched_skills) &&
        job.matched_skills.length > 0 && (

          <div className="mt-6">

            <h4 className="mb-2 text-sm font-semibold text-slate-300">
              Matched Skills
            </h4>

            <div className="flex flex-wrap gap-2">

              {job.matched_skills.map((skill, index) => (

                <span
                  key={`${skill}-${index}`}
                  className="rounded-lg bg-emerald-500/10 px-3 py-1.5 text-xs font-medium text-emerald-400"
                >
                  ✓ {skill}
                </span>

              ))}

            </div>

            {job?.classification === "Internship" &&
              Array.isArray(job?.matched_skill_evidence) &&
              job.matched_skill_evidence.some((item) => item.sources.includes("description")) && (
                <p className="mt-3 text-xs text-slate-400">
                  Skill evidence source: {job.matched_skill_evidence
                    .map((item) => `${item.skill} (${item.sources.join(" and ")})`)
                    .join(", ")}
                </p>
              )}

          </div>
        )}


      {/* ======================================================
          MISSING SKILLS
      ====================================================== */}
      {Array.isArray(job?.missing_skills) &&
        job.missing_skills.length > 0 && (

          <div className="mt-5">

            <h4 className="mb-2 text-sm font-semibold text-slate-300">
              Skills to Improve
            </h4>

            <div className="flex flex-wrap gap-2">

              {job.missing_skills.map((skill, index) => (

                <span
                  key={`${skill}-${index}`}
                  className="rounded-lg bg-red-500/10 px-3 py-1.5 text-xs font-medium text-red-400"
                >
                  + {skill}
                </span>

              ))}

            </div>

          </div>
        )}


      {/* ======================================================
          WHY RECOMMENDED
      ====================================================== */}
      {job?.why_recommended && (

        <div className="mt-6 rounded-xl border border-blue-500/20 bg-blue-500/5 p-4">

          <h4 className="mb-2 text-sm font-semibold text-blue-300">
            Why Recommended
          </h4>

          <p className="text-sm leading-6 text-slate-300">
            {job.why_recommended}
          </p>

        </div>

      )}

      {job?.classification === "Internship" && job?.role_evidence && (
        <p className="mt-3 text-xs leading-5 text-slate-400">
          {job.role_evidence}
        </p>
      )}


      {/* ======================================================
          JOB DESCRIPTION
      ====================================================== */}
      {job?.job_description && (

        <div className="mt-6">

          <h4 className="mb-2 text-sm font-semibold text-slate-300">
            Job Description
          </h4>

          <p className="line-clamp-4 text-sm leading-6 text-slate-400">
            {job.job_description}
          </p>

        </div>

      )}

    </article>
  )
}

export default JobCard