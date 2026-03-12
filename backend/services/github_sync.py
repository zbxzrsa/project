import httpx
from typing import List, Dict, Any, Optional
from datetime import datetime

from backend.services.github_client import GitHubClient
from backend.core.logging import logger


class RepositorySyncService:
    """SRS-006: System shall support repository synchronization"""
    
    def __init__(self, access_token: str):
        self.github_client = GitHubClient(access_token)
    
    async def sync_repository(
        self,
        owner: str,
        repo: str,
    ) -> Dict[str, Any]:
        """Sync repository branches and commits"""
        
        branches = await self._sync_branches(owner, repo)
        
        pull_requests = await self._sync_pull_requests(owner, repo)
        
        return {
            "branches": branches,
            "pull_requests": pull_requests,
            "synced_at": datetime.utcnow().isoformat(),
        }
    
    async def _sync_branches(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        """Fetch and sync branch information"""
        
        try:
            response = await self.github_client._request(
                "GET",
                f"/repos/{owner}/{repo}/branches"
            )
            
            branches = []
            for branch in response:
                branch_commit = await self.github_client._request(
                    "GET",
                    f"/repos/{owner}/{repo}/commits/{branch['commit']['sha']}"
                )
                
                branches.append({
                    "name": branch["name"],
                    "sha": branch["commit"]["sha"],
                    "protected": branch.get("protected", False),
                    "last_commit_message": branch_commit.get("commit", {}).get("message", "")[:200],
                    "last_commit_author": branch_commit.get("commit", {}).get("author", {}).get("name", ""),
                    "last_commit_date": branch_commit.get("commit", {}).get("author", {}).get("date", ""),
                })
            
            logger.info(f"Synced {len(branches)} branches for {owner}/{repo}")
            return branches
            
        except Exception as e:
            logger.error(f"Error syncing branches: {e}")
            return []
    
    async def _sync_pull_requests(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        """Fetch and sync pull request information"""
        
        try:
            response = await self.github_client._request(
                "GET",
                f"/repos/{owner}/{repo}/pulls",
                {"state": "all", "per_page": 50}
            )
            
            pull_requests = []
            for pr in response:
                pull_requests.append({
                    "number": pr["number"],
                    "title": pr["title"],
                    "state": pr["state"],
                    "head_branch": pr["head"]["ref"],
                    "base_branch": pr["base"]["ref"],
                    "head_sha": pr["head"]["sha"],
                    "author": pr["user"]["login"],
                    "created_at": pr["created_at"],
                    "updated_at": pr["updated_at"],
                    "merged_at": pr.get("merged_at"),
                })
            
            logger.info(f"Synced {len(pull_requests)} PRs for {owner}/{repo}")
            return pull_requests
            
        except Exception as e:
            logger.error(f"Error syncing PRs: {e}")
            return []
    
    async def get_branch_files(
        self,
        owner: str,
        repo: str,
        branch: str,
        path: str = "",
    ) -> List[Dict[str, Any]]:
        """Get files in a branch"""
        
        try:
            response = await self.github_client._request(
                "GET",
                f"/repos/{owner}/{repo}/contents/{path}",
                {"ref": branch}
            )
            
            if isinstance(response, list):
                return [
                    {
                        "name": item["name"],
                        "path": item["path"],
                        "type": item["type"],
                        "size": item.get("size", 0),
                    }
                    for item in response
                ]
            return []
            
        except Exception as e:
            logger.error(f"Error getting branch files: {e}")
            return []
    
    async def get_file_content(
        self,
        owner: str,
        repo: str,
        path: str,
        branch: str,
    ) -> Optional[str]:
        """Get file content from a branch"""
        
        try:
            content = await self.github_client.get_file_content(
                owner, repo, path, branch
            )
            return content
        except Exception as e:
            logger.error(f"Error getting file content: {e}")
            return None


class WebhookConfigService:
    """SRS-004: System shall configure GitHub webhooks for pull request events"""
    
    def __init__(self, access_token: str):
        self.github_client = GitHubClient(access_token)
        self.base_url = "https://api.github.com"
    
    async def create_webhook(
        self,
        owner: str,
        repo: str,
        webhook_url: str,
        secret: str,
    ) -> Dict[str, Any]:
        """Create a webhook for the repository"""
        
        config = {
            "url": webhook_url,
            "content_type": "json",
            "secret": secret,
        }
        
        events = ["pull_request", "push"]
        
        try:
            response = await self.github_client._request(
                "POST",
                f"/repos/{owner}/{repo}/hooks",
                {
                    "config": config,
                    "events": events,
                    "active": True,
                }
            )
            
            logger.info(f"Created webhook for {owner}/{repo}")
            return {
                "id": response["id"],
                "url": response["config"]["url"],
                "active": response["active"],
                "events": response["events"],
            }
            
        except Exception as e:
            logger.error(f"Error creating webhook: {e}")
            raise
    
    async def delete_webhook(
        self,
        owner: str,
        repo: str,
        webhook_id: int,
    ) -> bool:
        """Delete a webhook"""
        
        try:
            await self.github_client._request(
                "DELETE",
                f"/repos/{owner}/{repo}/hooks/{webhook_id}"
            )
            logger.info(f"Deleted webhook {webhook_id} for {owner}/{repo}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting webhook: {e}")
            return False
    
    async def list_webhooks(
        self,
        owner: str,
        repo: str,
    ) -> List[Dict[str, Any]]:
        """List all webhooks for a repository"""
        
        try:
            response = await self.github_client._request(
                "GET",
                f"/repos/{owner}/{repo}/hooks"
            )
            
            return [
                {
                    "id": hook["id"],
                    "url": hook["config"]["url"],
                    "active": hook["active"],
                    "events": hook["events"],
                    "created_at": hook["created_at"],
                }
                for hook in response
            ]
            
        except Exception as e:
            logger.error(f"Error listing webhooks: {e}")
            return []
    
    async def test_webhook(
        self,
        owner: str,
        repo: str,
        webhook_id: int,
    ) -> bool:
        """Test a webhook by sending a ping event"""
        
        try:
            await self.github_client._request(
                "POST",
                f"/repos/{owner}/{repo}/hooks/{webhook_id}/tests"
            )
            logger.info(f"Sent test ping to webhook {webhook_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error testing webhook: {e}")
            return False
