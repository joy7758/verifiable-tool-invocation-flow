"""Entrypoints for the secure tool invocation flow."""

from __future__ import annotations

import json
import os

from .flows.secure_tool_invocation_flow import SecureToolInvocationFlow


def kickoff():
    """Run the secure tool invocation flow and return its final summary."""
    flow = SecureToolInvocationFlow(output_dir=os.getenv("VTIF_OUTPUT_DIR"))
    return flow.kickoff()


def plot():
    """Render a flow plot when supported by the active flow runtime."""
    flow = SecureToolInvocationFlow(output_dir=os.getenv("VTIF_OUTPUT_DIR"))
    return flow.plot("secure_tool_invocation_flow")


def kickoff_cli() -> None:
    """Console-script wrapper that prints the flow summary and exits cleanly."""
    result = kickoff()
    if result is not None:
        print(json.dumps(result, indent=2, sort_keys=True))


def plot_cli() -> None:
    """Console-script wrapper for flow plotting."""
    plot()


if __name__ == "__main__":
    kickoff_cli()
