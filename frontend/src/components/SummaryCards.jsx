function SummaryCards({ summary }) {
  if (!summary) {
    return null
  }

  const cards = [
    {
      title: "Jobs Analyzed",
      value: summary.jobs_analyzed ?? 0,
      icon: "📊",
    },
    {
      title: "Jobs Recommended",
      value: summary.jobs_recommended ?? 0,
      icon: "🎯",
    },
    {
      title: "Excellent Matches",
      value: summary.excellent_matches ?? 0,
      icon: "⭐",
    },
    {
      title: "Strong Matches",
      value: summary.strong_matches ?? 0,
      icon: "💪",
    },
    {
      title: "Fresher Suitable",
      value: summary.fresher_suitable_jobs ?? 0,
      icon: "🌱",
    },
  ]

  return (
    <section className="mb-8">
      <h2 className="mb-4 text-xl font-semibold text-white">
        Recommendation Summary
      </h2>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-5">
        {cards.map((card) => (
          <div
            key={card.title}
            className="rounded-2xl border border-slate-800 bg-slate-900 p-5 shadow-lg"
          >
            <div className="mb-3 text-2xl">
              {card.icon}
            </div>

            <p className="text-sm text-slate-400">
              {card.title}
            </p>

            <p className="mt-1 text-2xl font-bold text-white">
              {card.value}
            </p>
          </div>
        ))}
      </div>
    </section>
  )
}

export default SummaryCards