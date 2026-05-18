"""Load ADK Skills and construct SkillToolsets for specialist agents."""

import pathlib

from google.adk.skills import load_skill_from_dir
from google.adk.tools.skill_toolset import SkillToolset

_SKILLS_DIR = pathlib.Path(__file__).resolve().parent


def load_skill_toolset(
    skill_name: str,
    additional_tools: list | None = None,
) -> SkillToolset:
    """Load a skill by directory name and wrap it in a SkillToolset.

    Args:
        skill_name: Name of the skill directory under skills/.
        additional_tools: Domain tools the agent needs (functions, BaseTool, AgentTool, etc.).
    """
    skill = load_skill_from_dir(str(_SKILLS_DIR / skill_name))
    return SkillToolset(
        skills=[skill],
        additional_tools=additional_tools,
    )
