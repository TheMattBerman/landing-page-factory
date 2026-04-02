#!/usr/bin/env python3
import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse


STAGES = [
    "site-extract",
    "page-strategy",
    "brand-profile",
    "page-copy",
    "page-visuals",
    "page-build",
    "page-qa",
]


MANUAL_STAGE_GUIDANCE = {
    "site-extract": {
        "artifacts": [
            "workspace/brand/extract.md",
            "workspace/brand/extract.json",
        ],
        "why": "Brand extract artifacts are missing and no source URL was provided for automated extraction.",
    },
    "firecrawl-setup": {
        "artifacts": [
            "FIRECRAWL_API_KEY configured in the environment or local .env",
        ],
        "why": "Firecrawl is not configured. For public-release-quality runs, extraction should pause until FIRECRAWL_API_KEY is available.",
    },
    "page-strategy": {
        "artifacts": [
            "workspace/pages/[page-name]/strategy.md",
            "workspace/pages/[page-name]/strategy.json",
        ],
        "why": "No strategy artifact exists yet. The pipeline cannot safely continue without mechanism, CTA, proof, and routing decisions.",
    },
    "brand-profile": {
        "artifacts": [
            "workspace/brand/profile.md",
            "workspace/brand/palette.json",
        ],
        "why": "Brand profile artifacts are missing. Copy, visuals, and build need the normalized voice and visual system.",
    },
    "page-copy": {
        "artifacts": [
            "workspace/pages/[page-name]/copy.md",
        ],
        "why": "Copy is still an authored stage. The builder should not fabricate page sections from thin metadata.",
    },
    "page-visuals": {
        "artifacts": [
            "workspace/pages/[page-name]/visuals/",
            "workspace/pages/[page-name]/visuals/manifest.json (recommended)",
        ],
        "why": "No visual package is available yet. The build stage needs either generated visuals or operator-supplied assets.",
    },
    "page-qa": {
        "artifacts": [
            "workspace/pages/[page-name]/qa.md",
        ],
        "why": "A final page-qa pass is still recommended even though the builder emits a QA scaffold.",
    },
}


def project_root() -> Path:
    env_root = os.environ.get("LPF_ROOT")
    if env_root:
        candidate = Path(env_root).expanduser().resolve()
        if (candidate / "AGENTS.md").exists() and (candidate / "workspace").exists():
            return candidate

    for candidate in [Path.cwd(), *Path.cwd().parents]:
        if (candidate / "AGENTS.md").exists() and (candidate / "workspace").exists():
            return candidate

    raise SystemExit("Could not locate project root")


def load_local_env(root: Path) -> dict[str, str]:
    env = os.environ.copy()
    env.setdefault("LPF_ROOT", str(root))

    env_path = root / ".env"
    if not env_path.exists():
        return env

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        if value and ((value[0] == value[-1]) and value[0] in {"'", '"'}):
            value = value[1:-1]
        env.setdefault(key, value)
    return env


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    return value


def unique_page_name(base: str, pages_dir: Path) -> str:
    candidate = base
    counter = 2
    while (pages_dir / candidate).exists():
        candidate = f"{base}-{counter}"
        counter += 1
    return candidate


def default_page_name(url: str | None, brand: str | None, audience: str | None, angle: str | None, pages_dir: Path) -> str:
    parts: list[str] = []
    if brand:
        parts.append(slugify(brand))
    elif url:
        hostname = urlparse(url).netloc.lower().replace("www.", "")
        parts.append(slugify(hostname.split(".")[0]))
    else:
        parts.append("landing-page")

    if audience:
        parts.append(slugify(audience))
    if angle:
        parts.append(slugify(angle))
    if not audience and not angle:
        parts.append("run")
    return unique_page_name("-".join(part for part in parts if part), pages_dir)


def stage_index(stage: str) -> int:
    return STAGES.index(stage)


def load_json(path: Path):
    if not path.exists():
        return None
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def extract_matches_url(extract_json: Path, url: str | None) -> bool:
    if not url or not extract_json.exists():
        return bool(extract_json.exists())
    payload = load_json(extract_json) or {}
    source = (payload.get("source") or "").strip().lower().rstrip("/")
    target = url.strip().lower().rstrip("/")
    return bool(source) and source == target


def page_artifacts(root: Path, page_name: str) -> dict[str, Path]:
    page_dir = root / "workspace" / "pages" / page_name
    return {
        "page_dir": page_dir,
        "extract_md": root / "workspace" / "brand" / "extract.md",
        "extract_json": root / "workspace" / "brand" / "extract.json",
        "profile_md": root / "workspace" / "brand" / "profile.md",
        "palette_json": root / "workspace" / "brand" / "palette.json",
        "strategy_md": page_dir / "strategy.md",
        "strategy_json": page_dir / "strategy.json",
        "copy_md": page_dir / "copy.md",
        "visuals_dir": page_dir / "visuals",
        "visual_manifest": page_dir / "visuals" / "manifest.json",
        "resolved_visuals": page_dir / "resolved-visuals.json",
        "image_slots": page_dir / "image-slots.json",
        "meta_json": page_dir / "meta.json",
        "html_image_context": page_dir / "html-image-context.json",
        "index_html": page_dir / "index.html",
        "qa_md": page_dir / "qa.md",
    }


def visual_package_present(paths: dict[str, Path]) -> bool:
    if paths["visual_manifest"].exists():
        return True
    visuals_dir = paths["visuals_dir"]
    if not visuals_dir.exists():
        return False
    for path in visuals_dir.iterdir():
        if path.is_file() and path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif"}:
            return True
    return False


def latest_visual_mtime(visuals_dir: Path) -> float:
    latest = 0.0
    if not visuals_dir.exists():
        return latest
    for path in visuals_dir.rglob("*"):
        if path.is_file():
            latest = max(latest, path.stat().st_mtime)
    return latest


def build_outputs_stale(paths: dict[str, Path]) -> bool:
    output_paths = [
        paths["resolved_visuals"],
        paths["meta_json"],
        paths["html_image_context"],
        paths["index_html"],
        paths["qa_md"],
    ]
    if any(not path.exists() for path in output_paths):
        return True

    newest_input = max(
        paths["strategy_json"].stat().st_mtime if paths["strategy_json"].exists() else 0.0,
        paths["copy_md"].stat().st_mtime if paths["copy_md"].exists() else 0.0,
        paths["profile_md"].stat().st_mtime if paths["profile_md"].exists() else 0.0,
        paths["palette_json"].stat().st_mtime if paths["palette_json"].exists() else 0.0,
        paths["visual_manifest"].stat().st_mtime if paths["visual_manifest"].exists() else 0.0,
        latest_visual_mtime(paths["visuals_dir"]),
    )
    oldest_output = min(path.stat().st_mtime for path in output_paths)
    return newest_input > oldest_output


def summarize_completed(output: str) -> str | None:
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    return lines[-1] if lines else None


def run_command(stage: str, cmd: list[str], *, cwd: Path, env: dict[str, str]) -> dict:
    completed = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True)
    result = {
        "stage": stage,
        "status": "completed" if completed.returncode == 0 else "failed",
        "command": " ".join(cmd),
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
        "summary": summarize_completed(completed.stdout) or summarize_completed(completed.stderr),
    }
    return result


def handoff(stage: str, page_name: str, url: str | None) -> dict:
    guidance = MANUAL_STAGE_GUIDANCE[stage]
    prompt_parts = [f"Run `{stage}` for `{page_name}`."]
    if url and stage in ("page-strategy", "firecrawl-setup"):
        prompt_parts.append(f"Source URL: {url}")
    prompt_parts.append(guidance["why"])
    prompt_parts.append("Write:")
    prompt_parts.extend(f"- {item.replace('[page-name]', page_name)}" for item in guidance["artifacts"])

    return {
        "stage": stage,
        "status": "needs-skill",
        "skill": stage if stage in STAGES else None,
        "why": guidance["why"],
        "artifacts": [item.replace("[page-name]", page_name) for item in guidance["artifacts"]],
        "prompt": "\n".join(prompt_parts),
    }


def build_chain_required(paths: dict[str, Path]) -> tuple[bool, str | None]:
    if not paths["strategy_json"].exists():
        return False, "page-strategy"
    if not paths["profile_md"].exists() or not paths["palette_json"].exists():
        return False, "brand-profile"
    if not paths["copy_md"].exists():
        return False, "page-copy"
    if not visual_package_present(paths):
        return False, "page-visuals"
    return True, None


def qa_verdict(path: Path) -> str | None:
    if not path.exists():
        return None
    match = re.search(r"^## Verdict\s*\n- ([^\n]+)", path.read_text(encoding="utf-8"), re.M)
    return match.group(1).strip() if match else None


def run_build_chain(root: Path, page_name: str, env: dict[str, str]) -> list[dict]:
    paths = page_artifacts(root, page_name)
    page_dir = paths["page_dir"]
    results = []

    results.append(
        run_command(
            "page-build",
            [
                sys.executable,
                str(root / "skills" / "page-build" / "scripts" / "resolve-visual-assets.py"),
                "--page-name",
                page_name,
                "--output",
                str(paths["resolved_visuals"]),
            ],
            cwd=root,
            env=env,
        )
    )
    if results[-1]["status"] != "completed":
        return results

    results.append(
        run_command(
            "page-build",
            [
                sys.executable,
                str(root / "skills" / "page-build" / "scripts" / "prepare-build-meta.py"),
                "--page-name",
                page_name,
                "--resolved-assets",
                str(paths["resolved_visuals"]),
                "--output",
                str(paths["meta_json"]),
            ],
            cwd=root,
            env=env,
        )
    )
    if results[-1]["status"] != "completed":
        return results

    results.append(
        run_command(
            "page-build",
            [
                sys.executable,
                str(root / "skills" / "page-build" / "scripts" / "select-build-images.py"),
                "--meta",
                str(paths["meta_json"]),
                "--output",
                str(paths["image_slots"]),
            ],
            cwd=root,
            env=env,
        )
    )
    if results[-1]["status"] != "completed":
        return results

    results.append(
        run_command(
            "page-build",
            [
                sys.executable,
                str(root / "skills" / "page-build" / "scripts" / "html-image-context.py"),
                "--meta",
                str(paths["meta_json"]),
                "--output",
                str(paths["html_image_context"]),
            ],
            cwd=root,
            env=env,
        )
    )
    if results[-1]["status"] != "completed":
        return results

    results.append(
        run_command(
            "page-build",
            [
                sys.executable,
                str(root / "skills" / "page-build" / "scripts" / "build-page.py"),
                "--page-name",
                page_name,
            ],
            cwd=root,
            env=env,
        )
    )
    if results[-1]["status"] != "completed":
        return results

    results.append(
        {
            "stage": "page-qa",
            "status": "completed" if paths["qa_md"].exists() else "needs-skill",
            "summary": "Builder QA scaffold written." if paths["qa_md"].exists() else "Run page-qa for a final review.",
        }
    )
    return results


def maybe_log_memory(root: Path, env: dict[str, str], *, enabled: bool, page_name: str, title: str, stages: list[dict], verdict: str | None) -> None:
    if not enabled:
        return
    completed_stages = ", ".join(stage["stage"] for stage in stages if stage.get("status") == "completed")
    subprocess.run(
        [
            sys.executable,
            str(root / "skills" / "landing-page-factory-orchestrator" / "scripts" / "page-admin.py"),
            "log-memory",
            "--title",
            title,
            "--page-name",
            page_name,
            "--stages",
            completed_stages or "none",
            "--verdict",
            verdict or "in-progress",
        ],
        cwd=root,
        env=env,
        capture_output=True,
        text=True,
    )


def format_markdown(payload: dict) -> str:
    lines = [
        f"# Orchestrator Run: {payload['page_name']}",
        "",
        f"- Status: `{payload['status']}`",
        f"- Next stage: `{payload['next_stage']}`",
        f"- Page dir: `{payload['page_dir']}`",
    ]
    if payload.get("source_url"):
        lines.append(f"- Source URL: `{payload['source_url']}`")
    if payload.get("qa_verdict"):
        lines.append(f"- QA verdict: `{payload['qa_verdict']}`")

    lines.extend(["", "## Stage Results"])
    for item in payload["stages"]:
        summary = item.get("summary") or item.get("why") or ""
        lines.append(f"- `{item['stage']}` — `{item['status']}`")
        if summary:
            lines.append(f"  {summary}")
        if item.get("command"):
            lines.append(f"  Command: `{item['command']}`")
        if item.get("artifacts"):
            lines.append("  Expected artifacts:")
            lines.extend(f"  - `{artifact}`" for artifact in item["artifacts"])

    return "\n".join(lines)


def run_pipeline(args: argparse.Namespace) -> dict:
    root = project_root()
    env = load_local_env(root)
    pages_dir = root / "workspace" / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)

    page_name = args.page_name or default_page_name(args.url, args.brand, args.audience, args.angle, pages_dir)
    paths = page_artifacts(root, page_name)
    paths["page_dir"].mkdir(parents=True, exist_ok=True)

    results: list[dict] = []
    target_index = stage_index(args.through)

    if target_index >= stage_index("site-extract"):
        extract_missing = not paths["extract_md"].exists() or not paths["extract_json"].exists()
        extract_mismatch = not extract_matches_url(paths["extract_json"], args.url)
        if extract_missing or args.force_extract:
            if not args.url:
                results.append(handoff("site-extract", page_name, args.url))
                return finalize(root, page_name, args.url, results, env, args)
            if not env.get("FIRECRAWL_API_KEY") and not args.allow_basic_extract:
                pause = handoff("firecrawl-setup", page_name, args.url)
                pause["summary"] = "Firecrawl is not configured. Add FIRECRAWL_API_KEY, then rerun. Use --allow-basic-extract only if you explicitly accept reduced extraction quality."
                results.append(pause)
                return finalize(root, page_name, args.url, results, env, args)

            extract_script = "firecrawl-extract.sh" if env.get("FIRECRAWL_API_KEY") else "basic-extract.sh"
            cmd = [
                "bash",
                str(root / "skills" / "site-extract" / "scripts" / extract_script),
                "--url",
                args.url,
                "--output",
                "workspace/brand",
            ]
            if extract_script == "basic-extract.sh" and args.deep:
                cmd.append("--deep")
            extract_result = run_command("site-extract", cmd, cwd=root, env=env)
            if extract_script == "basic-extract.sh" and extract_result["status"] == "completed":
                extract_result["summary"] = "Used basic extraction because FIRECRAWL_API_KEY is not configured. Recommend adding Firecrawl before public-release runs."
            results.append(extract_result)
            if extract_result["status"] != "completed":
                return finalize(root, page_name, args.url, results, env, args)
        elif args.url and extract_mismatch:
            if not env.get("FIRECRAWL_API_KEY") and not args.allow_basic_extract:
                pause = handoff("firecrawl-setup", page_name, args.url)
                pause["summary"] = "Existing extract does not match the requested URL, and Firecrawl is not configured. Add FIRECRAWL_API_KEY, then rerun. Use --allow-basic-extract only if you explicitly accept reduced extraction quality."
                results.append(pause)
                return finalize(root, page_name, args.url, results, env, args)
            extract_script = "firecrawl-extract.sh" if env.get("FIRECRAWL_API_KEY") else "basic-extract.sh"
            cmd = [
                "bash",
                str(root / "skills" / "site-extract" / "scripts" / extract_script),
                "--url",
                args.url,
                "--output",
                "workspace/brand",
            ]
            if extract_script == "basic-extract.sh" and args.deep:
                cmd.append("--deep")
            extract_result = run_command("site-extract", cmd, cwd=root, env=env)
            if extract_script == "basic-extract.sh" and extract_result["status"] == "completed":
                extract_result["summary"] = "Existing extract source did not match the requested URL, so extraction was refreshed with the basic extractor because FIRECRAWL_API_KEY is not configured."
            else:
                extract_result["summary"] = "Existing brand extract source did not match the requested URL, so extraction was refreshed."
            results.append(extract_result)
            if extract_result["status"] != "completed":
                return finalize(root, page_name, args.url, results, env, args)
        else:
            results.append(
                {
                    "stage": "site-extract",
                    "status": "completed",
                    "summary": "Brand extract artifacts already present.",
                }
            )
        if target_index == stage_index("site-extract"):
            return finalize(root, page_name, args.url, results, env, args)

    paths = page_artifacts(root, page_name)

    if target_index >= stage_index("page-strategy") and not paths["strategy_json"].exists():
        results.append(handoff("page-strategy", page_name, args.url))
        return finalize(root, page_name, args.url, results, env, args)

    if target_index >= stage_index("brand-profile") and (
        not paths["profile_md"].exists() or not paths["palette_json"].exists()
    ):
        results.append(handoff("brand-profile", page_name, args.url))
        return finalize(root, page_name, args.url, results, env, args)

    if target_index >= stage_index("page-copy") and not paths["copy_md"].exists():
        results.append(handoff("page-copy", page_name, args.url))
        return finalize(root, page_name, args.url, results, env, args)

    if target_index >= stage_index("page-visuals") and not visual_package_present(paths):
        results.append(handoff("page-visuals", page_name, args.url))
        return finalize(root, page_name, args.url, results, env, args)

    if target_index >= stage_index("page-build"):
        build_ready, blocking_stage = build_chain_required(paths)
        if not build_ready and blocking_stage:
            results.append(handoff(blocking_stage, page_name, args.url))
            return finalize(root, page_name, args.url, results, env, args)

        if args.force_build or build_outputs_stale(paths):
            results.extend(run_build_chain(root, page_name, env))
            if results[-1]["status"] == "failed":
                return finalize(root, page_name, args.url, results, env, args)
        else:
            results.append(
                {
                    "stage": "page-build",
                    "status": "completed",
                    "summary": "Build artifacts already present.",
                }
            )
            if target_index >= stage_index("page-qa"):
                results.append(
                    {
                        "stage": "page-qa",
                        "status": "completed" if paths["qa_md"].exists() else "needs-skill",
                        "summary": "QA scaffold already present." if paths["qa_md"].exists() else "Run page-qa for a final review.",
                    }
                )

    return finalize(root, page_name, args.url, results, env, args)


def finalize(root: Path, page_name: str, source_url: str | None, results: list[dict], env: dict[str, str], args: argparse.Namespace) -> dict:
    paths = page_artifacts(root, page_name)
    failing = next((item for item in results if item.get("status") == "failed"), None)
    needs_skill = next((item for item in results if item.get("status") == "needs-skill"), None)

    if failing:
        status = "failed"
        next_stage = failing["stage"]
    elif needs_skill:
        status = "paused_for_skill"
        next_stage = needs_skill["stage"]
    elif paths["qa_md"].exists():
        status = "ready_for_review"
        next_stage = "complete"
    elif stage_index(args.through) < stage_index("page-build"):
        status = "requested_stage_complete"
        next_stage = "complete"
    else:
        status = "in_progress"
        next_stage = "page-build"

    verdict = qa_verdict(paths["qa_md"])
    payload = {
        "page_name": page_name,
        "page_dir": str(paths["page_dir"]),
        "source_url": source_url,
        "status": status,
        "next_stage": next_stage,
        "qa_verdict": verdict,
        "generated_at": datetime.now().isoformat(),
        "stages": results,
    }

    maybe_log_memory(
        root,
        env,
        enabled=args.log_memory,
        page_name=page_name,
        title=args.memory_title or f"Pipeline run: {page_name}",
        stages=results,
        verdict=verdict or status,
    )
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the Landing Page Factory orchestrator pipeline until the next skill-authored stage or until build artifacts are complete."
    )
    parser.add_argument("--page-name")
    parser.add_argument("--url")
    parser.add_argument("--brand")
    parser.add_argument("--audience")
    parser.add_argument("--angle")
    parser.add_argument(
        "--through",
        choices=STAGES,
        default="page-qa",
        help="Highest stage to target in this run.",
    )
    parser.add_argument("--deep", action="store_true", help="Use deep mode when basic extraction is selected.")
    parser.add_argument("--force-extract", action="store_true")
    parser.add_argument("--force-build", action="store_true")
    parser.add_argument("--allow-basic-extract", action="store_true", help="Allow fallback to the basic extractor when Firecrawl is not configured.")
    parser.add_argument("--log-memory", action="store_true")
    parser.add_argument("--memory-title")
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    parser.add_argument("--output")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = run_pipeline(args)
    rendered = json.dumps(payload, indent=2) if args.format == "json" else format_markdown(payload)

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(rendered + ("\n" if not rendered.endswith("\n") else ""), encoding="utf-8")
    else:
        print(rendered)

    return 0 if payload["status"] != "failed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
