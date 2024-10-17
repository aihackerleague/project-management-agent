import toml
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession

def load_templates(templates_dir: str = "templates") -> dict[str, dict]:
    templates = {}
    for template_file in Path(templates_dir).glob("*.toml"):
        template_name = template_file.stem
        with open(template_file, "r") as f:
            templates[template_name] = toml.load(f)
    return templates

async def apply_template_to_issue(db: AsyncSession, issue_id: int, template_id: int) -> bool:
    # Implement the logic to apply a template to an issue
    # This function should:
    # 1. Load the template
    # 2. Get the issue
    # 3. Apply the template to the issue
    # 4. Update the issue in the database
    # 5. Return True if successful, False otherwise
    pass
import toml
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.template import Template
from ..schemas.template import TemplateCreate
from ..crud.template import create_template, get_templates, get_template
from ..crud.issue import get_issue

async def load_templates_to_db(db: AsyncSession, templates_dir: str = "templates") -> None:
    templates = {}
    for template_file in Path(templates_dir).glob("*.toml"):
        template_name = template_file.stem
        with open(template_file, "r") as f:
            template_content = toml.load(f)
            template_create = TemplateCreate(name=template_name, content=template_content)
            await create_template(db, template_create)

async def get_all_templates(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Template]:
    return await get_templates(db, skip=skip, limit=limit)

async def apply_template_to_issue(db: AsyncSession, issue_id: int, template_id: int) -> bool:
    try:
        template = await get_template(db, template_id)
        issue = await get_issue(db, issue_id)
        if template and issue:
            # Apply the template to the issue
            # This is where you would update the issue with the template content
            return True
    except Exception as e:
        print(f"Error applying template to issue: {e}")
    return False
