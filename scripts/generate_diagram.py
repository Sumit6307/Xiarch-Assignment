import os
from PIL import Image, ImageDraw, ImageFont

def generate_architecture_diagram():
    os.makedirs("docs", exist_ok=True)
    
    # Generate Mermaid documentation
    mermaid_content = """```mermaid
flowchart TD
    User([User / CLI / Web UI]) -->|1. Goal Prompt| Agent[Agent Core Execution Engine]
    
    subgraph Agent Core Framework
        Agent --> Planner[Dynamic Goal Planner & Decomposer]
        Agent --> Memory[Agent Working Memory & State Tracker]
        Agent --> SelfCorrect[Self-Correction & Reflection Engine]
    end

    Planner -->|2. Structured Step Plan| ToolReg[Tool Registry]

    subgraph Tool Orchestration Engine (4 Tools)
        ToolReg --> Tool1[Web Search Tool]
        ToolReg --> Tool2[Web Page Fetcher]
        ToolReg --> Tool3[Code Executor Sandbox]
        ToolReg --> Tool4[File Reader & Writer]
    end

    Tool1 -->|Observation| Agent
    Tool2 -->|Observation| Agent
    Tool3 -->|Observation| Agent
    Tool4 -->|Observation| Agent

    Tool1 -- Tool Error / Timeout --> SelfCorrect
    Tool2 -- HTTP 403 / Error --> SelfCorrect
    Tool3 -- Code Exception --> SelfCorrect
    
    SelfCorrect -->|3. Reflection & Recovery Plan| Planner

    Agent -->|4. Final Outputs| OutJSON[final_report.json]
    Agent -->|4. Final Outputs| OutMD[final_report.md]
```"""
    
    with open("docs/architecture.mermaid", "w", encoding="utf-8") as f:
        f.write(mermaid_content)

    # Render a high quality PNG architecture diagram using PIL
    width, height = 1100, 750
    image = Image.new("RGB", (width, height), color=(15, 23, 42)) # Dark navy background
    draw = ImageDraw.Draw(image)

    # Helper function to draw rounded boxes
    def draw_card(box, fill, outline, title, subtitle=""):
        x1, y1, x2, y2 = box
        draw.rounded_rectangle([x1, y1, x2, y2], radius=12, fill=fill, outline=outline, width=3)
        draw.text((x1 + 20, y1 + 15), title, fill=(248, 250, 252))
        if subtitle:
            draw.text((x1 + 20, y1 + 45), subtitle, fill=(148, 163, 184))

    # Draw Title Header
    draw.text((350, 30), "AGENTIC AI SYSTEM ARCHITECTURE", fill=(56, 189, 248))

    # User Interface Node
    draw_card((50, 100, 320, 190), (30, 41, 59), (56, 189, 248), "User / UI Interface", "CLI / Web Dashboard")

    # Core Agent Box
    draw.rounded_rectangle([380, 100, 1040, 320], radius=16, fill=(30, 41, 59), outline=(99, 102, 241), width=3)
    draw.text((410, 120), "Core Agent Execution Engine", fill=(129, 140, 248))
    
    # Submodules inside Agent
    draw_card((405, 170, 595, 290), (51, 65, 85), (56, 189, 248), "Planner Engine", "Goal Decomposition")
    draw_card((615, 170, 805, 290), (51, 65, 85), (234, 179, 8), "Self-Correction", "Reflection & Recovery")
    draw_card((825, 170, 1015, 290), (51, 65, 85), (34, 197, 94), "Working Memory", "Trace & State")

    # Tool Registry
    draw_card((380, 380, 1040, 580), (30, 41, 59), (168, 85, 247), "Multi-Tool Orchestration Engine", "4 Distinct Execution Tools")
    
    # 4 Tool Boxes inside Registry
    draw_card((400, 440, 540, 550), (51, 65, 85), (168, 85, 247), "Web Search", "DDG / Live HTTP")
    draw_card((555, 440, 695, 550), (51, 65, 85), (168, 85, 247), "Web Fetcher", "HTML Text Scraper")
    draw_card((710, 440, 850, 550), (51, 65, 85), (168, 85, 247), "Code Exec", "Python Sandbox")
    draw_card((865, 440, 1005, 550), (51, 65, 85), (168, 85, 247), "File Ops", "Report Reader/Writer")

    # Output Artifacts Node
    draw_card((380, 630, 1040, 710), (30, 41, 59), (34, 197, 94), "Structured Output Artifacts", "final_report.json  &  final_report.md")

    # Connectors / Arrows
    draw.line([(320, 145), (380, 145)], fill=(56, 189, 248), width=3) # UI -> Agent
    draw.line([(710, 320), (710, 380)], fill=(168, 85, 247), width=3) # Agent -> Tools
    draw.line([(710, 580), (710, 630)], fill=(34, 197, 94), width=3) # Tools -> Outputs

    image.save("docs/architecture_diagram.png")
    print("Successfully generated docs/architecture_diagram.png and docs/architecture.mermaid")

if __name__ == "__main__":
    generate_architecture_diagram()
