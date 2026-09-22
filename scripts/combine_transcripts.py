import os

def combine_transcripts():
    files = ["transcripts/sample_run_1_research.md", "transcripts/sample_run_2_failure_recovery.md", "transcripts/sample_run_3_code_analysis.md"]
    combined = ["# 📜 Combined Agent Execution Transcripts & Trace Logs\n"]
    
    for fpath in files:
        if os.path.exists(fpath):
            with open(fpath, "r", encoding="utf-8") as f:
                combined.append(f.read())
                combined.append("\n\n---\n\n")

    with open("transcripts/all_sample_transcripts.md", "w", encoding="utf-8") as f:
        f.write("\n".join(combined))
    print("Combined transcripts saved to transcripts/all_sample_transcripts.md")

if __name__ == "__main__":
    combine_transcripts()
