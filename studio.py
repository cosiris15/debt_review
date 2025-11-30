"""
LangGraph Studio Entry Point

This file exposes the debt review workflow to LangGraph Studio
for visual debugging and interactive testing.

Usage:
    1. Start Studio server: langgraph dev
    2. Open LangGraph Studio app or visit https://smith.langchain.com
    3. Connect to http://127.0.0.1:2024
"""

from app.agents.workflow import build_workflow
from app.agents.state import WorkflowState, create_initial_state

# Build and compile the workflow graph
# This is the object that LangGraph Studio will visualize
graph = build_workflow().compile()


def create_test_state(
    creditor_name: str = "测试债权人",
    bankruptcy_date: str = "2024-02-26",
    materials_path: str = ""
) -> WorkflowState:
    """
    Helper to create test state from Studio interface.

    Args:
        creditor_name: Name of the creditor to test
        bankruptcy_date: Bankruptcy acceptance date (YYYY-MM-DD)
        materials_path: Path to creditor's claim materials

    Returns:
        Initial workflow state ready for execution

    Example:
        In Studio, you can call this with real test data:
        create_test_state(
            creditor_name="上海牧诚贸易有限公司",
            materials_path="/Users/chenchu/Desktop/第1批债权/债权申报书-上海牧诚贸易有限公司.md"
        )
    """
    return create_initial_state(
        task_id="studio-test-001",
        project_id="studio-project",
        project_config={
            "bankruptcy_date": bankruptcy_date,
            "interest_stop_date": "2024-02-25",
            "debtor_name": "上海欧卡罗家居有限公司"
        },
        creditors=[{
            "id": "test-creditor-001",
            "creditor_name": creditor_name,
            "batch_number": 1,
            "creditor_number": 1,
            "materials_path": materials_path,
            "output_path": "./outputs/test"
        }]
    )


# Pre-built test states for common testing scenarios
TEST_STATES = {
    "muchen": create_test_state(
        creditor_name="上海牧诚贸易有限公司",
        materials_path="/Users/chenchu/Desktop/第1批债权/债权申报书-上海牧诚贸易有限公司.md"
    ),
    "baoxin": create_test_state(
        creditor_name="上海宝信软件股份有限公司",
        materials_path="/Users/chenchu/Desktop/第1批债权/债权申报书-上海宝信软件股份有限公司.md"
    ),
    "chengying": create_test_state(
        creditor_name="上海成盈贸易有限公司",
        materials_path="/Users/chenchu/Desktop/第1批债权/债权申报书-上海成盈贸易有限公司.md"
    )
}


if __name__ == "__main__":
    # Quick verification that graph compiles correctly
    print("Workflow graph compiled successfully!")
    print(f"Graph nodes: {list(graph.nodes.keys())}")
    print(f"Entry point: init")
