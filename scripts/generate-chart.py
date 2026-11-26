#!/usr/bin/env python3
"""Universal Helm chart generator for getting-started-todo-app-openai-agent.

Supports generating charts for:
  - local_kind   (compose-prod-build.yml -> charts/getting-started-todo-app-openai-agent.local_kind)
  - github_kind  (compose-prod-GitHub.yml -> charts/getting-started-todo-app-openai-agent.github_kind)
  - gcp_gke      (compose-prod-GCPRegistry.yml -> charts/getting-started-todo-app-openai-agent.gcp_gke)
  - all          (generates all 3 charts above)

Usage:
  python scripts/generate-chart.py [local_kind | github_kind | gcp_gke | all]
"""
import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
KATENARY = REPO / "katenary.exe"
PROJECT_DIR_NAME = "getting-started-todo-app-openai-agent"
DEFAULT_ICON = "https://raw.githubusercontent.com/cstpeace0191/getting-started-todo-app-openAI-agent/main/client/public/favicon.ico"

ENV_CONFIGS = {
    "local_kind": {
        "compose": REPO / "compose-prod-build.yml" if (REPO / "compose-prod-build.yml").is_file() else REPO / "compose-local_kind.yaml",
        "chart": REPO / "charts" / "getting-started-todo-app-openai-agent.local_kind",
    },
    "github_kind": {
        "compose": REPO / "compose-prod-GitHub.yml" if (REPO / "compose-prod-GitHub.yml").is_file() else REPO / "compose-github_kind.yaml",
        "chart": REPO / "charts" / "getting-started-todo-app-openai-agent.github_kind",
    },
    "gcp_gke": {
        "compose": REPO / "compose-prod-GCPRegistry.yml" if (REPO / "compose-prod-GCPRegistry.yml").is_file() else REPO / "compose-gcp_gke.yaml",
        "chart": REPO / "charts" / "getting-started-todo-app-openai-agent.gcp_gke",
    },
}


def generate_single_chart(target: str, app_version: str = "1.0.0", chart_version: str = "0.1.0") -> int:
    config = ENV_CONFIGS.get(target)
    if not config:
        print(f"ERROR: Unknown target '{target}'. Valid targets: {list(ENV_CONFIGS.keys())}", file=sys.stderr)
        return 1

    source_compose = config["compose"]
    chart_out = config["chart"]

    if not source_compose.is_file():
        print(f"ERROR: Compose file '{source_compose}' not found", file=sys.stderr)
        return 1

    katenary_bin = str(KATENARY) if KATENARY.is_file() else "katenary"

    with tempfile.TemporaryDirectory() as tmp:
        project = Path(tmp) / PROJECT_DIR_NAME
        project.mkdir()
        shutil.copyfile(source_compose, project / "compose.yaml")

        cmd = [
            katenary_bin, "convert",
            "-o", str(chart_out),
            "-a", app_version,
            "-v", chart_version,
            "-i", DEFAULT_ICON,
            "-f",
        ]
        result = subprocess.run(cmd, cwd=project)
        if result.returncode != 0:
            return result.returncode

    # Apply backend service type patch
    patch = REPO / "scripts" / "patch-service-type.py"
    if patch.is_file():
        ret = subprocess.run([sys.executable, str(patch), str(chart_out)], cwd=REPO).returncode
        if ret != 0:
            return ret

    # Synchronize production manifests and templates
    sync_script = REPO / "scripts" / "sync_charts.py"
    if sync_script.is_file():
        ret = subprocess.run([sys.executable, str(sync_script)], cwd=REPO).returncode
        if ret != 0:
            return ret

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Helm charts with Katenary")
    parser.add_argument("target", nargs="?", default="all",
                        choices=["local_kind", "github_kind", "gcp_gke", "all"],
                        help="Target environment (default: all)")
    parser.add_argument("-a", "--app-version", default="1.0.0", help="Application version")
    parser.add_argument("-v", "--chart-version", default="0.1.0", help="Chart version")

    args = parser.parse_args()

    targets = list(ENV_CONFIGS.keys()) if args.target == "all" else [args.target]

    for t in targets:
        print(f"\n==========================================")
        print(f" Generating Helm chart: {t}")
        print(f"==========================================")
        code = generate_single_chart(t, args.app_version, args.chart_version)
        if code != 0:
            print(f"FAILED to generate chart for {t}", file=sys.stderr)
            return code

    print("\n[SUCCESS] All requested charts generated and patched successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

