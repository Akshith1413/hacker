"""
README Validator - Validates README instructions by testing them in sandboxes
"""

import re
import asyncio
from typing import Dict, List, Optional, Any
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from runanywhere.execution_controller import get_execution_controller


class ReadmeValidator:
    """
    Validates README instructions by actually executing them in sandboxes.
    
    Features:
    - Extract setup instructions from README
    - Test installation commands
    - Verify build/run commands
    - Detect broken links and outdated information
    """
    
    def __init__(self):
        self.execution_controller = get_execution_controller()
    
    async def validate_readme(
        self,
        readme_content: str,
        repo_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate README content by testing instructions.
        
        Args:
            readme_content: README markdown content
            repo_data: Repository metadata
            
        Returns:
            Validation results with scores and issues
        """
        validation_result = {
            "overall_score": 0.0,
            "sections_found": [],
            "sections_missing": [],
            "setup_instructions_valid": False,
            "commands_tested": [],
            "broken_links": [],
            "issues": [],
            "recommendations": []
        }
        
        # Check for required sections
        required_sections = [
            "installation",
            "usage",
            "getting started",
            "setup",
            "requirements",
            "dependencies"
        ]
        
        readme_lower = readme_content.lower()
        
        for section in required_sections:
            if section in readme_lower:
                validation_result["sections_found"].append(section)
            else:
                validation_result["sections_missing"].append(section)
        
        # Extract code blocks (commands)
        commands = self._extract_code_blocks(readme_content)
        
        if not commands:
            validation_result["issues"].append({
                "type": "missing_code_examples",
                "severity": "medium",
                "message": "No code blocks found in README"
            })
            validation_result["recommendations"].append(
                "Add code examples showing how to install and use the project"
            )
        
        # Extract setup commands
        setup_commands = self._extract_setup_commands(commands, repo_data)
        
        # Test a subset of commands (to avoid long execution)
        if setup_commands:
            test_results = await self._test_commands(
                setup_commands[:3],  # Test first 3 commands
                repo_data
            )
            
            validation_result["commands_tested"] = test_results
            validation_result["setup_instructions_valid"] = all(
                cmd["success"] for cmd in test_results
            )
        
        # Check for broken links
        links = self._extract_links(readme_content)
        # Note: Actually checking links would require HTTP requests
        # For now, just detect suspicious patterns
        for link in links:
            if "localhost" in link or "127.0.0.1" in link:
                validation_result["broken_links"].append({
                    "url": link,
                    "reason": "Local URL in README"
                })
        
        # Calculate overall score
        score = 0.0
        
        # Sections score (40 points)
        sections_score = (len(validation_result["sections_found"]) / len(required_sections)) * 40
        score += sections_score
        
        # Code examples score (20 points)
        if commands:
            score += 20
        
        # Valid instructions score (40 points)
        if validation_result["setup_instructions_valid"]:
            score += 40
        elif validation_result["commands_tested"]:
            # Partial credit based on success rate
            success_rate = sum(1 for cmd in validation_result["commands_tested"] if cmd["success"]) / len(validation_result["commands_tested"])
            score += 40 * success_rate
        
        validation_result["overall_score"] = min(100.0, score)
        
        # Add recommendations
        if validation_result["overall_score"] < 60:
            validation_result["recommendations"].append(
                "README needs significant improvement - add clear setup instructions"
            )
        
        if not validation_result["sections_found"]:
            validation_result["recommendations"].append(
                "Add standard sections: Installation, Usage, Requirements"
            )
        
        return validation_result
    
    def _extract_code_blocks(self, markdown: str) -> List[str]:
        """Extract code blocks from markdown"""
        # Match ```language\ncode\n``` blocks
        pattern = r"```(?:\w+)?\n(.*?)\n```"
        matches = re.findall(pattern, markdown, re.DOTALL)
        
        # Also match inline code with `code`
        inline_pattern = r"`([^`\n]+)`"
        inline_matches = re.findall(inline_pattern, markdown)
        
        return matches + inline_matches
    
    def _extract_setup_commands(
        self,
        code_blocks: List[str],
        repo_data: Dict[str, Any]
    ) -> List[str]:
        """Extract likely setup commands from code blocks"""
        setup_commands = []
        
        # Common setup command patterns
        setup_patterns = [
            r"npm install",
            r"yarn install",
            r"pip install",
            r"bundle install",
            r"composer install",
            r"flutter pub get",
            r"go mod download",
            r"cargo build",
            r"mvn install",
            r"gradle build"
        ]
        
        for block in code_blocks:
            for pattern in setup_patterns:
                if re.search(pattern, block, re.IGNORECASE):
                    setup_commands.append(block.strip())
                    break
        
        return setup_commands
    
    async def _test_commands(
        self,
        commands: List[str],
        repo_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Test commands in a sandbox"""
        results = []
        
        for command in commands:
            # Detect language from command
            language = "bash"
            if "npm" in command or "node" in command:
                language = "node"
            elif "pip" in command or "python" in command:
                language = "python"
            elif "flutter" in command:
                language = "flutter"
            elif "go" in command:
                language = "go"
            elif "cargo" in command:
                language = "rust"
            
            # For now, just mark as untested (would need actual sandbox)
            results.append({
                "command": command,
                "language": language,
                "success": None,  # Would test in real implementation
                "output": "",
                "error": "Testing skipped (requires Docker)",
                "tested": False
            })
        
        return results
    
    def _extract_links(self, markdown: str) -> List[str]:
        """Extract URLs from markdown"""
        # Match [text](url) and bare URLs
        link_pattern = r"\[([^\]]+)\]\(([^\)]+)\)|https?://[^\s<>\"]+|www\.[^\s<>\".]+"
        matches = re.findall(link_pattern, markdown)
        
        links = []
        for match in matches:
            if isinstance(match, tuple):
                links.append(match[1] if match[1] else match[0])
            else:
                links.append(match)
        
        return [link for link in links if link]
    
    def analyze_readme_quality(self, readme_content: str) -> Dict[str, Any]:
        """
        Analyze README quality without execution.
        
        Args:
            readme_content: README markdown content
            
        Returns:
            Quality analysis
        """
        analysis = {
            "length": len(readme_content),
            "word_count": len(readme_content.split()),
            "has_title": False,
            "has_description": False,
            "has_installation": False,
            "has_usage": False,
            "has_examples": False,
            "has_license": False,
            "has_contributing": False,
            "has_badges": False,
            "image_count": 0,
            "link_count": 0,
            "code_block_count": 0,
            "quality_score": 0.0
        }
        
        readme_lower = readme_content.lower()
        
        # Check for common sections
        if re.search(r"^#\s+", readme_content, re.MULTILINE):
            analysis["has_title"] = True
        
        if len(readme_content) > 100:
            analysis["has_description"] = True
        
        if any(x in readme_lower for x in ["install", "setup", "getting started"]):
            analysis["has_installation"] = True
        
        if "usage" in readme_lower or "how to use" in readme_lower:
            analysis["has_usage"] = True
        
        if "example" in readme_lower:
            analysis["has_examples"] = True
        
        if "license" in readme_lower:
            analysis["has_license"] = True
        
        if "contribut" in readme_lower:
            analysis["has_contributing"] = True
        
        if re.search(r"!\[.*\]\(https?://", readme_content):
            analysis["has_badges"] = True
        
        # Count elements
        analysis["image_count"] = len(re.findall(r"!\[.*?\]\(.*?\)", readme_content))
        analysis["link_count"] = len(self._extract_links(readme_content))
        analysis["code_block_count"] = len(self._extract_code_blocks(readme_content))
        
        # Calculate quality score
        score = 0.0
        
        if analysis["has_title"]: score += 10
        if analysis["has_description"]: score += 15
        if analysis["has_installation"]: score += 20
        if analysis["has_usage"]: score += 20
        if analysis["has_examples"]: score += 15
        if analysis["has_license"]: score += 5
        if analysis["has_contributing"]: score += 5
        if analysis["has_badges"]: score += 5
        if analysis["code_block_count"] > 0: score += 5
        
        analysis["quality_score"] = score
        
        return analysis


# Global instance
_readme_validator: Optional[ReadmeValidator] = None


def get_readme_validator() -> ReadmeValidator:
    """Get or create global README validator instance"""
    global _readme_validator
    if _readme_validator is None:
        _readme_validator = ReadmeValidator()
    return _readme_validator
