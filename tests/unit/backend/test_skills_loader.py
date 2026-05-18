"""Unit tests for skills.loader — ADK skill loading."""
import pytest

ALL_SKILLS = [
    "fitness", "meal", "sleep", "habit", "task", "school",
    "longterm", "reading", "relationships", "news", "finance", "trivial",
]

SKILLS_WITH_REFERENCES = [
    "fitness", "meal", "sleep", "habit", "school",
    "longterm", "reading", "relationships", "finance",
]

SKILLS_WITHOUT_REFERENCES = ["task", "news", "trivial"]


class TestLoadAllSkills:
    @pytest.mark.parametrize("skill_name", ALL_SKILLS)
    def test_load_skill_no_error(self, skill_name):
        from google.adk.skills import load_skill_from_dir
        import pathlib

        skills_dir = pathlib.Path(__file__).resolve().parents[3] / "src" / "assistant" / "skills"
        skill = load_skill_from_dir(str(skills_dir / skill_name))
        assert skill is not None
        assert skill.name == skill_name

    @pytest.mark.parametrize("skill_name", ALL_SKILLS)
    def test_skill_has_nonempty_instructions(self, skill_name):
        from google.adk.skills import load_skill_from_dir
        import pathlib

        skills_dir = pathlib.Path(__file__).resolve().parents[3] / "src" / "assistant" / "skills"
        skill = load_skill_from_dir(str(skills_dir / skill_name))
        assert skill.instructions and len(skill.instructions.strip()) > 0


class TestSkillReferences:
    @pytest.mark.parametrize("skill_name", SKILLS_WITH_REFERENCES)
    def test_skills_with_references_have_files(self, skill_name):
        import pathlib

        skills_dir = pathlib.Path(__file__).resolve().parents[3] / "src" / "assistant" / "skills"
        refs_dir = skills_dir / skill_name / "references"
        assert refs_dir.is_dir(), f"Missing references/ for {skill_name}"
        ref_files = list(refs_dir.glob("*.md"))
        assert len(ref_files) > 0, f"No .md files in references/ for {skill_name}"

    @pytest.mark.parametrize("skill_name", SKILLS_WITHOUT_REFERENCES)
    def test_skills_without_references(self, skill_name):
        import pathlib

        skills_dir = pathlib.Path(__file__).resolve().parents[3] / "src" / "assistant" / "skills"
        refs_dir = skills_dir / skill_name / "references"
        assert not refs_dir.is_dir() or len(list(refs_dir.glob("*.md"))) == 0


class TestSkillToolsetLoader:
    def test_load_skill_toolset_success(self):
        from skills.loader import load_skill_toolset

        toolset = load_skill_toolset("fitness")
        assert toolset is not None

    def test_invalid_skill_raises(self):
        from skills.loader import load_skill_toolset

        with pytest.raises((FileNotFoundError, Exception)):
            load_skill_toolset("nonexistent_skill_xyz")

    def test_additional_tools_accepted(self):
        from skills.loader import load_skill_toolset

        def dummy_tool():
            pass

        toolset = load_skill_toolset("trivial", additional_tools=[dummy_tool])
        assert toolset is not None
