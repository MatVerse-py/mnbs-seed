"""
MatVerse Skills - Skills Operadoras para GitHub Actions
================================================================================
Skills baseadas no UMJAM.txt para integração com GitHub:
- Repo Discovery
- Code Navigation
- PR Review
- Issue Management
- Engineering Copilot
- Setup Organization

Autor: MiniMax Agent
================================================================================
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable
from enum import Enum

from ..ledger import SkillType, SkillOperator, SkillAction


# ================================================================================
# GITHUB ACTIONS
# ================================================================================

@dataclass
class GitHubAction:
    """Ação GitHub"""
    name: str
    endpoint: str
    method: str = "GET"
    description: str = ""
    required_scopes: List[str] = field(default_factory=list)


# Ações disponíveis (baseadas em UMJAM.txt)
GITHUB_ACTIONS = {
    # Repo Discovery
    "check_repo_initialized": GitHubAction(
        name="check_repo_initialized",
        endpoint="/repos/{owner}/{repo}",
        description="Verificar se repo existe",
        required_scopes=["repo"]
    ),
    "get_repo": GitHubAction(
        name="get_repo",
        endpoint="/repos/{owner}/{repo}",
        description="Obter metadados do repo"
    ),
    "search_branches": GitHubAction(
        name="search_branches",
        endpoint="/repos/{owner}/{repo}/branches",
        description="Buscar branches"
    ),
    "fetch_commit": GitHubAction(
        name="fetch_commit",
        endpoint="/repos/{owner}/{repo}/commits/{ref}",
        description="Obter commit"
    ),
    "get_commit_combined_status": GitHubAction(
        name="get_commit_combined_status",
        endpoint="/commits/{owner}/{repo}/{ref}/status",
        description="Status combinado do commit"
    ),

    # Code Navigation
    "search": GitHubAction(
        name="search",
        endpoint="/search/code",
        description="Buscar código"
    ),
    "fetch_file": GitHubAction(
        name="fetch_file",
        endpoint="/repos/{owner}/{repo}/contents/{path}",
        description="Obter arquivo"
    ),
    "fetch_blob": GitHubAction(
        name="fetch_blob",
        endpoint="/git/blobs/{sha}",
        description="Obter blob por SHA"
    ),

    # PR Review
    "get_pr_info": GitHubAction(
        name="get_pr_info",
        endpoint="/pulls/{owner}/{repo}/{number}",
        description="Obter info do PR"
    ),
    "get_pr_diff": GitHubAction(
        name="get_pr_diff",
        endpoint="/pulls/{owner}/{repo}/{number}",
        description="Obter diff do PR"
    ),
    "fetch_pr_patch": GitHubAction(
        name="fetch_pr_patch",
        endpoint="/pulls/{owner}/{repo}/{number}",
        description="Obter patch do PR"
    ),
    "list_pr_changed_filenames": GitHubAction(
        name="list_pr_changed_filenames",
        endpoint="/pulls/{owner}/{repo}/{number}/files",
        description="Listar arquivos alterados"
    ),
    "fetch_pr_comments": GitHubAction(
        name="fetch_pr_comments",
        endpoint="/pulls/{owner}/{repo}/{number}/comments",
        description="Obter comentários do PR"
    ),

    # Issue Management
    "list_recent_issues": GitHubAction(
        name="list_recent_issues",
        endpoint="/issues",
        description="Listar issues recentes"
    ),
    "fetch_issue": GitHubAction(
        name="fetch_issue",
        endpoint="/repos/{owner}/{repo}/issues/{number}",
        description="Obter issue"
    ),
    "search_issues": GitHubAction(
        name="search_issues",
        endpoint="/search/issues",
        description="Buscar issues"
    ),

    # Engineering Copilot
    "get_users_recent_prs_in_repo": GitHubAction(
        name="get_users_recent_prs_in_repo",
        endpoint="/repos/{owner}/{repo}/pulls",
        description="PRs recentes do usuário"
    ),
    "get_user_login": GitHubAction(
        name="get_user_login",
        endpoint="/user",
        description="Obter login do usuário"
    ),
    "get_profile": GitHubAction(
        name="get_profile",
        endpoint="/users/{username}",
        description="Obter perfil"
    ),
    "list_user_orgs": GitHubAction(
        name="list_user_orgs",
        endpoint="/user/orgs",
        description="Listar organizações do usuário"
    ),

    # Setup Organization
    "list_repositories": GitHubAction(
        name="list_repositories",
        endpoint="/user/repos",
        description="Listar repositórios"
    ),
    "search_repositories": GitHubAction(
        name="search_repositories",
        endpoint="/search/repositories",
        description="Buscar repositórios"
    ),
    "get_repo_collaborator_permission": GitHubAction(
        name="get_repo_collaborator_permission",
        endpoint="/repos/{owner}/{repo}/collaborators/{username}/permission",
        description="Obter permissão de colaborador"
    )
}


# ================================================================================
# SKILL IMPLEMENTATIONS
# ================================================================================

class RepoDiscoverySkill(SkillOperator):
    """Skill: Descobrir contexto do repo"""

    def __init__(self):
        super().__init__(
            skill_type=SkillType.REPO_DISCOVERY,
            name="Repo Discovery",
            description="Mapear estrutura e contexto de repositórios",
            actions=[
                SkillAction(a.name, GITHUB_ACTIONS[a.name].description)
                for a in [
                    GITHUB_ACTIONS["check_repo_initialized"],
                    GITHUB_ACTIONS["get_repo"],
                    GITHUB_ACTIONS["search_branches"],
                    GITHUB_ACTIONS["fetch_commit"],
                    GITHUB_ACTIONS["get_commit_combined_status"]
                ]
            ]
        )

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        result = super().execute(context)
        result['objective'] = "Entender se o repo existe, branch padrão, status CI"
        result['github_actions'] = [a.name for a in self.actions]
        return result


class CodeNavigationSkill(SkillOperator):
    """Skill: Navegar e compreender código"""

    def __init__(self):
        super().__init__(
            skill_type=SkillType.CODE_NAVIGATION,
            name="Code Navigation",
            description="Leitura rápida e localização de código",
            actions=[
                SkillAction(a.name, GITHUB_ACTIONS[a.name].description)
                for a in [
                    GITHUB_ACTIONS["search"],
                    GITHUB_ACTIONS["fetch_file"],
                    GITHUB_ACTIONS["fetch_blob"]
                ]
            ]
        )

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        result = super().execute(context)
        result['objective'] = "Leitura rápida, localizar onde modificar"
        return result


class PRReviewSkill(SkillOperator):
    """Skill: Entender mudanças (PRs)"""

    def __init__(self):
        super().__init__(
            skill_type=SkillType.PR_REVIEW,
            name="PR Review",
            description="Revisão de Pull Requests",
            actions=[
                SkillAction(a.name, GITHUB_ACTIONS[a.name].description)
                for a in [
                    GITHUB_ACTIONS["get_pr_info"],
                    GITHUB_ACTIONS["get_pr_diff"],
                    GITHUB_ACTIONS["fetch_pr_patch"],
                    GITHUB_ACTIONS["list_pr_changed_filenames"],
                    GITHUB_ACTIONS["fetch_pr_comments"]
                ]
            ]
        )

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        result = super().execute(context)
        result['objective'] = "Revisão de PR, análise de risco, qualidade"
        return result


class IssueManagementSkill(SkillOperator):
    """Skill: Gestão de trabalho (issues)"""

    def __init__(self):
        super().__init__(
            skill_type=SkillType.ISSUE_MANAGEMENT,
            name="Issue Management",
            description="Triagem e priorização de issues",
            actions=[
                SkillAction(a.name, GITHUB_ACTIONS[a.name].description)
                for a in [
                    GITHUB_ACTIONS["list_recent_issues"],
                    GITHUB_ACTIONS["fetch_issue"],
                    GITHUB_ACTIONS["search_issues"]
                ]
            ]
        )

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        result = super().execute(context)
        result['objective'] = "Triagem, sumarização, priorização"
        return result


class EngineeringCopilotSkill(SkillOperator):
    """Skill: Meu trabalho recente"""

    def __init__(self):
        super().__init__(
            skill_type=SkillType.ENGINEERING_COPILOT,
            name="Engineering Copilot",
            description="Copiloto de engenharia pessoal",
            actions=[
                SkillAction(a.name, GITHUB_ACTIONS[a.name].description)
                for a in [
                    GITHUB_ACTIONS["get_users_recent_prs_in_repo"],
                    GITHUB_ACTIONS["get_user_login"],
                    GITHUB_ACTIONS["get_profile"],
                    GITHUB_ACTIONS["list_user_orgs"]
                ]
            ]
        )

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        result = super().execute(context)
        result['objective'] = "Copiloto de engenharia pessoal"
        return result


class SetupOrganizationSkill(SkillOperator):
    """Skill: Setup/organização"""

    def __init__(self):
        super().__init__(
            skill_type=SkillType.SETUP_ORGANIZATION,
            name="Setup Organization",
            description="Mapear ecossistema e permissões",
            actions=[
                SkillAction(a.name, GITHUB_ACTIONS[a.name].description)
                for a in [
                    GITHUB_ACTIONS["list_repositories"],
                    GITHUB_ACTIONS["search_repositories"],
                    GITHUB_ACTIONS["get_repo_collaborator_permission"]
                ]
            ]
        )

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        result = super().execute(context)
        result['objective'] = "Mapear ecossistema e permissões"
        return result


# ================================================================================
# SKILL REGISTRY
# ================================================================================

class SkillRegistry:
    """Registro central de skills"""

    _skills: Dict[SkillType, SkillOperator] = {}

    @classmethod
    def register(cls, skill: SkillOperator):
        cls._skills[skill.skill_type] = skill

    @classmethod
    def get(cls, skill_type: SkillType) -> Optional[SkillOperator]:
        return cls._skills.get(skill_type)

    @classmethod
    def get_all(cls) -> Dict[SkillType, SkillOperator]:
        return cls._skills.copy()

    @classmethod
    def initialize(cls):
        """Inicializa registro com todas as skills"""
        cls.register(RepoDiscoverySkill())
        cls.register(CodeNavigationSkill())
        cls.register(PRReviewSkill())
        cls.register(IssueManagementSkill())
        cls.register(EngineeringCopilotSkill())
        cls.register(SetupOrganizationSkill())


# Inicializa
SkillRegistry.initialize()


# ================================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # GitHub Actions
    "GitHubAction",
    "GITHUB_ACTIONS",

    # Skills
    "RepoDiscoverySkill",
    "CodeNavigationSkill",
    "PRReviewSkill",
    "IssueManagementSkill",
    "EngineeringCopilotSkill",
    "SetupOrganizationSkill",

    # Registry
    "SkillRegistry"
]
