"""
Multi-LLM Alignment Demo
Author: John B. Carroll Jr.
Framework: Feedback Processor Theory / Trinity Harmonics
Purpose: Show convergence of outputs from multiple LLMs using harmonic feedback
"""

from harmonic_feedback import harmonic_feedback, trinity_return
import numpy as np

# --- Simulated LLM outputs (numerical embeddings or scalar proxies) ---
# Example: 3 LLMs responding to the same prompt
llm_outputs = {
    "GPT":    [0.85, 0.87, 0.83, 0.86],
    "Claude": [0.78, 0.80, 0.81, 0.79],
    "Gemini": [0.82, 0.83, 0.81, 0.82]
}

# --- Convert to harmonic space using trinity_return ---
def harmonize_llm_outputs(outputs_dict):
    aligned_results = {}
    for llm, values in outputs_dict.items():
        aligned_results[llm] = trinity_return(values)
    return aligned_results

# --- Visualization ---
def print_alignment(results):
    print("=== Multi-LLM Alignment Demo ===")
    for llm, data in results.items():
        final_values = [r["final"] for r in data]
        print(f"{llm} final harmonic outputs: {final_values}")

# --- Run Demo ---
if __name__ == "__main__":
    aligned = harmonize_llm_outputs(llm_outputs)
    print_alignment(aligned)

    # Optional: compute pairwise convergence metric
    all_final = np.array([ [r["final"] for r in aligned[llm]] for llm in llm_outputs ])
    mean_vector = np.mean(all_final, axis=0)
    deviation = np.mean(np.abs(all_final - mean_vector))
    print(f"\nAverage deviation from mean alignment: {deviation:.6f}")