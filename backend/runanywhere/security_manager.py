"""
Security Manager - Handles security policies and resource limits for sandboxes
"""

import re
from typing import Dict, List, Optional, Any


class SecurityManager:
    """
    Manages security policies for code execution in sandboxes.
    
    Features:
    - Code pattern validation
    - Resource limit enforcement
    - Malicious code detection
    - Network policy management
    """
    
    # Patterns that indicate potentially dangerous code
    DANGEROUS_PATTERNS = {
        "python": [
            r"import\s+os",
            r"import\s+subprocess",
            r"import\s+sys",
            r"__import__",
            r"eval\s*\(",
            r"exec\s*\(",
            r"compile\s*\(",
            r"open\s*\(",
            r"file\s*\(",
        ],
        "javascript": [
            r"require\s*\(\s*['\"]child_process['\"]",
            r"require\s*\(\s*['\"]fs['\"]",
            r"eval\s*\(",
            r"Function\s*\(",
            r"process\.exit",
            r"process\.kill",
        ],
        "bash": [
            r"rm\s+-rf",
            r"mkfs",
            r"dd\s+if=",
            r":\(\)\{.*\}",  # Fork bomb
            r"curl.*\|.*bash",
            r"wget.*\|.*sh",
        ]
    }
    
    # Safe patterns that are allowed
    SAFE_PATTERNS = {
        "python": [
            r"import\s+math",
            r"import\s+random",
            r"import\s+datetime",
            r"import\s+json",
            r"from\s+typing",
        ]
    }
    
    def __init__(self):
        self.max_memory_mb = 2048
        self.max_cpu_cores = 4
        self.max_execution_time = 300  # 5 minutes
        self.max_network_bandwidth_mbps = 10
    
    def validate_code(
        self,
        code: str,
        language: str,
        strict_mode: bool = True
    ) -> Dict[str, Any]:
        """
        Validate code for security issues.
        
        Args:
            code: Code to validate
            language: Programming language
            strict_mode: Enable strict validation
            
        Returns:
            Validation result with issues and risk level
        """
        issues = []
        risk_level = "safe"
        
        # Check for dangerous patterns
        dangerous_patterns = self.DANGEROUS_PATTERNS.get(language.lower(), [])
        
        for pattern in dangerous_patterns:
            matches = re.findall(pattern, code, re.IGNORECASE | re.MULTILINE)
            if matches:
                issues.append({
                    "type": "dangerous_pattern",
                    "pattern": pattern,
                    "matches": matches,
                    "severity": "high" if strict_mode else "medium"
                })
                risk_level = "high"
        
        # Check code length
        if len(code) > 100000:  # 100KB
            issues.append({
                "type": "code_too_large",
                "size": len(code),
                "severity": "medium"
            })
            risk_level = max(risk_level, "medium", key=lambda x: ["safe", "low", "medium", "high"].index(x))
        
        # Check for excessive loops (naive check)
        loop_patterns = [
            r"while\s+True",
            r"while\s+1",
            r"for\s+.*\s+in\s+range\s*\(\s*\d{6,}",  # Huge range
        ]
        
        for pattern in loop_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                issues.append({
                    "type": "potential_infinite_loop",
                    "pattern": pattern,
                    "severity": "medium"
                })
                risk_level = max(risk_level, "medium", key=lambda x: ["safe", "low", "medium", "high"].index(x))
        
        return {
            "is_safe": risk_level != "high" or not strict_mode,
            "risk_level": risk_level,
            "issues": issues,
            "strict_mode": strict_mode
        }
    
    def get_resource_limits(
        self,
        execution_type: str = "standard"
    ) -> Dict[str, Any]:
        """
        Get resource limits based on execution type.
        
        Args:
            execution_type: Type of execution (snippet, repo, batch)
            
        Returns:
            Resource limit configuration
        """
        limits = {
            "snippet": {
                "memory_mb": 256,
                "cpu_cores": 0.5,
                "timeout_seconds": 30,
                "network_enabled": False,
                "disk_mb": 100
            },
            "repo": {
                "memory_mb": 1024,
                "cpu_cores": 2.0,
                "timeout_seconds": 300,
                "network_enabled": True,
                "disk_mb": 1000
            },
            "batch": {
                "memory_mb": 2048,
                "cpu_cores": 4.0,
                "timeout_seconds": 600,
                "network_enabled": True,
                "disk_mb": 2000
            },
            "readme_test": {
                "memory_mb": 512,
                "cpu_cores": 1.0,
                "timeout_seconds": 120,
                "network_enabled": True,
                "disk_mb": 500
            }
        }
        
        return limits.get(execution_type, limits["snippet"])
    
    def sanitize_command(self, command: str) -> str:
        """
        Sanitize a shell command to prevent injection attacks.
        
        Args:
            command: Shell command to sanitize
            
        Returns:
            Sanitized command
        """
        # Remove dangerous characters
        dangerous_chars = [";", "&", "|", "`", "$", "(", ")", "<", ">", "\n", "\r"]
        
        sanitized = command
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, "")
        
        return sanitized.strip()
    
    def validate_repository_url(self, repo_url: str) -> bool:
        """
        Validate that a repository URL is safe to clone.
        
        Args:
            repo_url: Repository URL
            
        Returns:
            True if safe, False otherwise
        """
        # Check for GitHub/GitLab/Bitbucket URLs
        safe_domains = [
            r"github\.com",
            r"gitlab\.com",
            r"bitbucket\.org"
        ]
        
        for domain in safe_domains:
            if re.search(domain, repo_url, re.IGNORECASE):
                return True
        
        return False
    
    def get_network_policy(
        self,
        allow_external: bool = True
    ) -> Dict[str, Any]:
        """
        Get network policy configuration.
        
        Args:
            allow_external: Allow external network access
            
        Returns:
            Network policy configuration
        """
        if not allow_external:
            return {
                "enabled": False,
                "allowed_domains": [],
                "blocked_domains": ["*"],
                "max_bandwidth_mbps": 0
            }
        
        return {
            "enabled": True,
            "allowed_domains": [
                "github.com",
                "gitlab.com",
                "npmjs.com",
                "pypi.org",
                "maven.org",
                "crates.io",
                "pub.dev"
            ],
            "blocked_domains": [
                "*.onion",
                "*.i2p"
            ],
            "max_bandwidth_mbps": self.max_network_bandwidth_mbps
        }
    
    def check_rate_limit(
        self,
        user_id: str,
        executions_per_hour: int = 100
    ) -> Dict[str, Any]:
        """
        Check if user has exceeded rate limits.
        
        Args:
            user_id: User identifier
            executions_per_hour: Maximum executions per hour
            
        Returns:
            Rate limit status
        """
        # TODO: Implement actual rate limiting with Redis or in-memory cache
        # For now, return always allowed
        return {
            "allowed": True,
            "remaining": executions_per_hour,
            "reset_at": None,
            "limit": executions_per_hour
        }
    
    def audit_log_execution(
        self,
        execution_id: str,
        user_id: str,
        code_hash: str,
        language: str,
        result: Dict[str, Any]
    ) -> None:
        """
        Log execution for security audit.
        
        Args:
            execution_id: Execution identifier
            user_id: User identifier
            code_hash: Hash of executed code
            language: Programming language
            result: Execution result
        """
        # TODO: Implement actual audit logging
        # For now, just print
        print(f"[AUDIT] Execution {execution_id} by {user_id}: {language} ({code_hash})")


# Global security manager instance
_security_manager: Optional[SecurityManager] = None


def get_security_manager() -> SecurityManager:
    """Get or create global security manager instance"""
    global _security_manager
    if _security_manager is None:
        _security_manager = SecurityManager()
    return _security_manager
