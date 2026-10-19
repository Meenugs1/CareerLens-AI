import { useState } from "react"
import { parseSkillInput } from "../utils/skillInput"

function SearchForm({ onSearch, onReset, loading }) {
  const [role, setRole] = useState("")
  const [skills, setSkills] = useState("")
  const [experience, setExperience] = useState("0")
  const [location, setLocation] = useState("Any")
  const [workMode, setWorkMode] = useState("Any")
  const [jobType, setJobType] = useState("Any")

  const handleSubmit = (e) => {
    e.preventDefault()

    const skillList = parseSkillInput(skills)

    onSearch({
      role: role.trim(),
      skills: skillList,
      experience: Number(experience) || 0,
      location: location.trim() || "Any",
      work_mode: workMode,
      job_type: jobType,
    })
  }

  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-xl">
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-white">
          Find Your Best-Matched Jobs
        </h2>

        <p className="mt-1 text-sm text-slate-400">
          Enter your profile details and get personalized recommendations.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">

        {/* Job Role */}
        <div>
          <label className="mb-2 block text-sm font-medium text-slate-300">
            Target Job Role
          </label>

          <input
            type="text"
            value={role}
            onChange={(e) => setRole(e.target.value)}
            placeholder="e.g. Data Analyst"
            required
            className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition placeholder:text-slate-500 focus:border-blue-500"
          />
        </div>

        {/* Skills */}
        <div>
          <label className="mb-2 block text-sm font-medium text-slate-300">
            Your Skills
          </label>

          <input
            type="text"
            value={skills}
            onChange={(e) => setSkills(e.target.value)}
            placeholder="Python, SQL, Excel, Power BI"
            required
            className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition placeholder:text-slate-500 focus:border-blue-500"
          />

          <p className="mt-2 text-xs text-slate-500">
            Separate multiple skills with commas.
          </p>
        </div>

        {/* Experience + Location */}
        <div className="grid gap-5 md:grid-cols-2">

          {/* Experience */}
          <div>
            <label className="mb-2 block text-sm font-medium text-slate-300">
              Experience (Years)
            </label>

            <input
              type="number"
              min="0"
              step="0.5"
              value={experience}
              onChange={(e) => setExperience(e.target.value)}
              className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none focus:border-blue-500"
            />
          </div>

          {/* Location */}
          <div>
            <label className="mb-2 block text-sm font-medium text-slate-300">
              Preferred Location
            </label>

            <input
              type="text"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="Bengaluru or Any"
              className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none placeholder:text-slate-500 focus:border-blue-500"
            />
          </div>
        </div>

        {/* Work Mode */}
        <div>
          <label className="mb-2 block text-sm font-medium text-slate-300">
            Preferred Work Mode
          </label>

          <select
            value={workMode}
            onChange={(e) => setWorkMode(e.target.value)}
            className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none focus:border-blue-500"
          >
            <option value="Any">Any</option>
            <option value="On-site">On-site</option>
            <option value="Hybrid">Hybrid</option>
            <option value="Remote">Remote</option>
          </select>
        </div>

        {/* Job Type */}
        <div>
          <label className="mb-2 block text-sm font-medium text-slate-300">
            Job Type
          </label>

          <select
            value={jobType}
            onChange={(e) => setJobType(e.target.value)}
            className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none focus:border-blue-500"
          >
            <option value="Any">Any</option>
            <option value="Full-time">Full-time</option>
            <option value="Internship">Internship</option>
            <option value="Trainee">Trainee</option>
          </select>
        </div>

        {/* Submit */}
        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-xl bg-blue-600 px-5 py-3.5 font-semibold text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading ? "Finding Best Jobs..." : "🔎 Recommend Jobs"}
        </button>

        <button
          type="button"
          onClick={onReset}
          disabled={loading}
          className="w-full rounded-xl border border-slate-700 px-5 py-3.5 font-semibold text-slate-300 transition hover:border-slate-600 hover:text-white disabled:cursor-not-allowed disabled:opacity-50"
        >
          Reset
        </button>

      </form>
    </section>
  )
}

export default SearchForm