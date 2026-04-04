# mini_demo/run_mini_audit.py
import os
import sys
from dotenv import load_dotenv

# 1. LOAD ENVIRONMENT FIRST!
load_dotenv("Backend/.env")

# Ensure we can import from Backend
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "Backend")))

from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.toolkits import FileToolkit, TerminalToolkit
from camel.societies.workforce import Workforce
from camel.tasks import Task
from camel.types import ModelPlatformType, ModelType
from camel.models import ModelFactory

def run_mini_audit():
    print("🚀 Starting ACRO Mini Demo (Gemini 2.0 Flash stable)...")
    
    # Check if API Key is loaded
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ ERROR: GEMINI_API_KEY not found in Backend/.env")
        return

    # 2. Setup Gemini Model (Gemini 2.0 Flash)
    try:
        model = ModelFactory.create(
            model_platform=ModelPlatformType.GEMINI,
            model_type="gemini-2.0-flash", 
        )
    except Exception as e:
        print(f"❌ ERROR Creating Model: {e}")
        return
    
    target_path = os.path.abspath("mini_demo")
    
    # 3. Setup Agents
    auditor_sys_msg = BaseMessage.make_assistant_message(
        role_name="Auditor",
        content="Briefly analyze 'app.py' and 'pyproject.toml' for security risks and outdated dependencies. Be very concise."
    )
    auditor = ChatAgent(auditor_sys_msg, model=model, tools=FileToolkit(working_directory=target_path).get_tools())
    
    fixer_sys_msg = BaseMessage.make_assistant_message(
        role_name="Fixer",
        content="Fix detected issues in 'app.py' and 'pyproject.toml' concisely using the terminal. Minimal talk."
    )
    fixer = ChatAgent(fixer_sys_msg, model=model, tools=[
        *FileToolkit(working_directory=target_path).get_tools(),
        *TerminalToolkit(working_directory=target_path).get_tools()
    ])
    
    strategist_sys_msg = BaseMessage.make_assistant_message(
        role_name="Strategist",
        content="Create a simple, non-parallel plan: 1. Audit, 2. Fix, 3. Verify. Do not run tasks in parallel."
    )
    strategist = ChatAgent(strategist_sys_msg, model=model)
    
    # 4. Create Workforce
    print("🧠 Initializing Workforce...")
    workforce = Workforce(
        "Mini-ACRO", 
        coordinator_agent=strategist,
        task_agent=strategist
    )
    
    workforce.add_single_agent_worker(description="Auditor: Concisely detects vulnerabilities.", worker=auditor)
    workforce.add_single_agent_worker(description="Fixer: Patches code and runs terminal installs.", worker=fixer)
    
    # 5. Define Task (Simplified to avoid path duplication)
    task_content = (
        "Perform a sequential vulnerability audit and fix: "
        "First, identify if pyproject.toml has an old fastapi version and update it to 0.109.0 in the terminal. "
        "Second, remove hardcoded admin credentials from app.py. "
        "Third, verify the changes."
    )
    
    print(f"📋 Task: {task_content}\n")
    task = Task(content=task_content)
    result = workforce.process_task(task)
    
    print("\n✅ MISSION COMPLETE!")
    print(f"Summary: {result.result}")

if __name__ == "__main__":
    run_mini_audit()
