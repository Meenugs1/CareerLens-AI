function Header({ activeView, onNavigate }) {
  return (
    <header className="border-b border-slate-800 bg-slate-950">
      <div className="mx-auto max-w-7xl px-6 py-5">
        <div className="header-inner flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">
              CareerLens AI
            </h1>

            <p className="mt-1 text-sm text-slate-400">
              Smart job recommendations powered by your skills
            </p>
          </div>

          <nav className="header-nav flex items-center gap-2" aria-label="Primary navigation">
            <button
              className={`header-nav-button ${activeView === "home" ? "active" : ""}`}
              type="button"
              onClick={() => onNavigate("home")}
            >
              Explore Jobs
            </button>
            <button
              className={`header-nav-button ${activeView === "market" ? "active" : ""}`}
              type="button"
              onClick={() => onNavigate("market")}
            >
              Market Intelligence
            </button>
            <button
              className={`header-nav-button ${activeView === "skill-gap" ? "active" : ""}`}
              type="button"
              onClick={() => onNavigate("skill-gap")}
            >
              Skill Gap
            </button>
            <button
              className={`header-nav-button ${activeView === "simulator" ? "active" : ""}`}
              type="button"
              onClick={() => onNavigate("simulator")}
            >
              Career Simulator
            </button>
            <button
              className={`header-nav-button ${activeView === "switch" ? "active" : ""}`}
              type="button"
              onClick={() => onNavigate("switch")}
            >
              Career Switch
            </button>
            <button
              className={`header-nav-button ${activeView === "career-path" ? "active" : ""}`}
              type="button"
              onClick={() => onNavigate("career-path")}
            >
              Career Path
            </button>
            <button
              className={`header-nav-button ${activeView === "what-can-i-become" ? "active" : ""}`}
              type="button"
              onClick={() => onNavigate("what-can-i-become")}
            >
              What Can I Become?
            </button>
            <button
              className={`header-nav-button ${activeView === "company-intelligence" ? "active" : ""}`}
              type="button"
              onClick={() => onNavigate("company-intelligence")}
            >
              Company Intelligence
            </button>
          </nav>
        </div>
      </div>
    </header>
  );
}

export default Header;