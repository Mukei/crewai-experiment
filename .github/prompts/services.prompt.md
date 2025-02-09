{
    "project_rules": {
        "bug_fixing": {
            "require_analysis": true,
            "document_root_cause": true,
            "validate_solution": true
        },
        "code_quality": {
            "prioritize_readability": true,
            "avoid_over_engineering": true,
            "prefer_standard_libraries": true,
            "mandatory_comments": true
        },
        "documentation": {
            "decision_file": {
                "required": true,
                "path": "docs/decision.md",
                "validate_against_history": true
            }
        },
        "change_management": {
            "require_plan": true,
            "single_file_changes": true,
            "prevent_unrelated_changes": true,
            "mandatory_testing": true
        }
    },
    "tech_stack": {
        "package_management": {
            "pixi": {
                "enabled": true,
                "validate_pixi_yaml": true,
                "auto_generate_lock": true
            }
        },
        "environment": {
            "dotenv": {
                "required": true,
                "template_provided": true
            }
        }
    },
    "enable_snippet_suggestions": true,
    "enable_inline_suggestions": true,
    "enable_autocompletion": true,
    "framework_detection": {
        "python": true,
        "crew_ai": true,
        "ollama": true
    },
    "code_style": {
        "python": {
            "max_line_length": 88,
            "use_black": true,
            "sort_imports": true
        }
    },
    "project_structure": {
        "src": {
            "agents": true,
            "tasks": true,
            "tools": true,
            "guardrails": true
        },
        "tests": true,
        "config": true,
        "docs": {
            "decision_md": true,
            "api_docs": true
        }
    },
    "lsp": {
        "python": {
            "pylint": true,
            "mypy": true,
            "black": true,
            "isort": true
        }
    },
    "snippets": {
        "crew_ai": {
            "agent_template": true,
            "task_template": true,
            "tool_template": true
        },
        "ollama": {
            "model_config": true,
            "api_calls": true
        },
        "nemo_guardrails": {
            "config_template": true,
            "rule_template": true
        },
        "pixi": {
            "pixi_yaml_template": true,
            "dependency_snippets": true
        }
    },
    "git": {
        "enable": true,
        "commit_message_template": "feat(${scope}): ${message}",
        "branch_naming": "feature/${name}",
        "pre_commit_hooks": {
            "test_execution": true,
            "decision_md_validation": true
        }
    },
    "testing": {
        "enable_pytest": true,
        "generate_tests": true,
        "test_template": true,
        "run_after_changes": true
    }
}