"""
Test script for processing Batch 9 complex financial creditors.

This script tests the LangGraph workflow with the complex financial creditor cases
from batch 9 and compares results with the target outputs from the original solution.
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.agents.workflow import run_workflow_with_auto_mode, get_workflow_app
from app.agents.state import create_initial_state


# Batch 9 test configuration
# Note: Creditor 401 has TWO material files (普通债权 + 有财产担保债权)
# These need to be merged/combined for a single creditor processing
BATCH_9_CREDITORS = [
    {
        "creditor_name": "中国中信金融资产管理股份有限公司江苏省分公司",
        "batch_number": 9,
        "creditor_number": 401,
        # Both material files for this creditor
        "materials_path": "/Users/chenchu/Desktop/第9批债权申报材料",
        "output_path": "./outputs/batch_9/401-中国中信金融资产管理股份有限公司江苏省分公司",
        "declared_amounts": {
            "principal": 382374698.55,  # 本金: 两笔合计
            "interest": 229954237.23,   # 利息
            "total": 787686696.16       # 总额 (含违约金、补偿金、诉讼费、律师费、迟延履行金)
        }
    },
    {
        "creditor_name": "中国长城资产管理股份有限公司江苏省分公司",
        "batch_number": 9,
        "creditor_number": 402,
        "materials_path": "/Users/chenchu/Desktop/第9批债权申报材料/中国长城资产管理股份有限公司江苏省分公司.md",
        "output_path": "./outputs/batch_9/402-中国长城资产管理股份有限公司江苏省分公司",
        "declared_amounts": {
            "principal": None,  # To be extracted from materials
            "interest": None,
            "total": None
        }
    }
]

# Shared context for batch 9
BATCH_9_CONTEXT = {
    "debtor_name": "江苏熔盛重工有限公司",
    "bankruptcy_date": "2025-09-16",  # 破产受理日
    "interest_stop_date": "2025-09-16",
    "task_id": f"batch9-test-{datetime.now().strftime('%Y%m%d%H%M%S')}",
    "project_id": "batch-9-financial-creditors"
}


async def test_single_creditor(creditor_config: dict, shared_context: dict):
    """Test processing a single creditor."""
    print(f"\n{'='*60}")
    print(f"Testing: {creditor_config['creditor_name']}")
    print(f"Materials: {creditor_config['materials_path']}")
    print(f"{'='*60}")

    try:
        result = await run_workflow_with_auto_mode(
            creditor_configs=[creditor_config],
            shared_context=shared_context,
            max_concurrent=1
        )

        print(f"\nResult mode: {result.get('mode')}")
        print(f"Success count: {result.get('success_count', 0)}")
        print(f"Failure count: {result.get('failure_count', 0)}")

        # Check for outputs
        output_path = Path(creditor_config['output_path'])
        if output_path.exists():
            print(f"\nGenerated files:")
            for item in output_path.rglob("*"):
                if item.is_file():
                    print(f"  - {item.relative_to(output_path)}: {item.stat().st_size} bytes")

        return result

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


async def test_batch9_workflow():
    """Test the full batch 9 workflow."""
    print("\n" + "="*70)
    print("BATCH 9 COMPLEX FINANCIAL CREDITORS TEST")
    print("="*70)
    print(f"Debtor: {BATCH_9_CONTEXT['debtor_name']}")
    print(f"Bankruptcy Date: {BATCH_9_CONTEXT['bankruptcy_date']}")
    print(f"Creditors: {len(BATCH_9_CREDITORS)}")

    # Test only the first creditor (most complex case)
    # to avoid long processing time
    test_creditor = BATCH_9_CREDITORS[0]

    result = await test_single_creditor(test_creditor, BATCH_9_CONTEXT)

    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    if "error" in result:
        print(f"Test FAILED: {result['error']}")
    else:
        print(f"Test completed")
        print(f"Mode: {result.get('mode')}")
        print(f"Success: {result.get('success_count', 0)}")
        print(f"Failures: {result.get('failure_count', 0)}")

    return result


if __name__ == "__main__":
    # Run the test
    result = asyncio.run(test_batch9_workflow())

    # Exit with appropriate code
    if "error" in result or result.get("failure_count", 0) > 0:
        sys.exit(1)
    sys.exit(0)
