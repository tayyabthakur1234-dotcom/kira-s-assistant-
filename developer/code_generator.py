"""
Code Generator Module - KIRA AI Operating System (Phase 10)
Generates high-quality, production-ready source code, classes, functions, APIs,
tests, documentation, comments, and examples across 18 programming languages and frameworks.
"""

import os
import json
from typing import Dict, Any, List, Optional
from utils.logger import logger
from router.model_router import model_router


class CodeGenerator:
    def __init__(self, workspace_root: str = "."):
        self.workspace_root = os.path.abspath(workspace_root)
        self.supported_languages = [
            "Python", "JavaScript", "TypeScript", "React", "Next.js", "Node.js",
            "HTML", "CSS", "Tailwind", "C++", "C#", "Java", "Go", "Rust",
            "PHP", "SQL", "Shell", "PowerShell"
        ]

    async def generate_code(
        self,
        prompt: str,
        language: str = "TypeScript",
        component_type: str = "file", # file, class, function, api, test, doc, comment, example
        target_path: Optional[str] = None,
        context_files: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Generates software artifacts using Gemini/Grok model router and optionally writes them to disk."""
        lang_str = language if language in self.supported_languages else "TypeScript"
        
        system_prompt = f"""You are KIRA, a Senior Principal Software Engineer and Architect.
Your task is to generate complete, clean, modular, production-ready code in {lang_str}.
Follow best practices for {lang_str}:
- Use clear variable and function names.
- Include proper error handling and input validation.
- Include JSDoc / Docstring comments for public APIs.
- Do NOT use stub placeholders or 'TODO' comments.
- Format properly with standard indentation.

Output ONLY a JSON object with the following schema:
{{
    "title": "Name of the component or file",
    "language": "{lang_str}",
    "filepath": "Suggested file relative path e.g. src/components/MyComponent.tsx",
    "code": "The complete generated source code",
    "explanation": "Brief senior engineer design explanation",
    "usage_example": "Code snippet showing how to import and use this artifact",
    "test_snippet": "Unit test code for this artifact"
}}
"""

        user_prompt = f"Target Component Type: {component_type}\nInstruction: {prompt}\nTarget Path: {target_path or 'auto'}"
        if context_files:
            user_prompt += f"\nContext Files: {', '.join(context_files)}"

        # Call AI model router
        res = await model_router.execute_with_failover(
            prompt=user_prompt,
            category="coding",
            system_instruction=system_prompt
        )

        output_text = res.get("response", "")
        # Try parsing JSON output
        parsed_data = self._extract_json(output_text, lang_str, target_path, prompt)

        # Write to disk if path requested
        saved_file = None
        if target_path and parsed_data.get("code"):
            full_dest = os.path.join(self.workspace_root, target_path)
            try:
                os.makedirs(os.path.dirname(full_dest), exist_ok=True)
                with open(full_dest, 'w', encoding='utf-8') as f:
                    f.write(parsed_data["code"])
                saved_file = target_path
                logger.info(f"CodeGenerator wrote file: {saved_file}")
            except Exception as e:
                logger.error(f"Failed writing generated code to {target_path}: {e}")

        return {
            "status": "success",
            "language": lang_str,
            "component_type": component_type,
            "target_path": target_path,
            "saved_file": saved_file,
            "artifact": parsed_data,
            "model_used": res.get("model_used")
        }

    def _extract_json(self, text: str, lang: str, target_path: Optional[str], prompt: str) -> Dict[str, Any]:
        """Extracts JSON block from model response or creates fallback structured response."""
        try:
            # Match JSON inside ```json ... ```
            if "```json" in text:
                json_str = text.split("```json")[1].split("```")[0].strip()
                return json.loads(json_str)
            elif "```" in text:
                # Extract code directly if formatted in triple backticks
                raw_code = text.split("```")[1].split("```")[0].strip()
                if raw_code.startswith(("typescript", "javascript", "python", "tsx", "jsx", "go", "rust", "cpp")):
                    raw_code = "\n".join(raw_code.splitlines()[1:])
                return {
                    "title": f"Generated {lang} Artifact",
                    "language": lang,
                    "filepath": target_path or f"src/generated_{lang.lower().replace('.', '')}_artifact",
                    "code": raw_code,
                    "explanation": "Generated code artifact based on model instructions.",
                    "usage_example": "// Import and invoke as standard module",
                    "test_snippet": "// Test suite template"
                }
            else:
                return json.loads(text.strip())
        except Exception:
            return {
                "title": f"Generated {lang} Code",
                "language": lang,
                "filepath": target_path or "src/generated_code.ts",
                "code": text,
                "explanation": "Generated software component.",
                "usage_example": f"// Usage example for {prompt[:30]}",
                "test_snippet": "// Unit tests"
            }


code_generator = CodeGenerator()
