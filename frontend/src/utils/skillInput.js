export function parseSkillInput(value) {
  const seen = new Set();

  return value
    .split(",")
    .map((skill) => skill.trim())
    .filter((skill) => {
      const key = skill.toLowerCase();
      if (!skill || seen.has(key)) {
        return false;
      }

      seen.add(key);
      return true;
    });
}