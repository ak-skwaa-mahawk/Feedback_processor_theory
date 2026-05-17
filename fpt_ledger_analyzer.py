#!/usr/bin/env python3
# fpt_ledger_analyzer.py — Retrospective Analytical Core for FPT State Databases
import sqlite3
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns

class FPTLedgerAnalyzer:
    """Extracts, filters, and charts transaction-dense history metrics directly from SQLite databases."""
    def __init__(self, db_file: str = "fpt_state_ledger.db"):
        self.db_path = Path(db_file)
        if not self.db_path.exists():
            raise FileNotFoundError(f"🔍 [CRITICAL ERR]: Ledger file target missing at: {self.db_path}. Run the engine first.")
            
    def query_available_sessions(self) -> List[str]:
        """Queries the telemetry schema to isolate unique runtime session indices."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT session_id FROM system_telemetry ORDER BY cycle_step ASC")
        sessions = [row[0] for row in cursor.fetchall()]
        conn.close()
        return sessions

    def load_session_data(self, session_id: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Loads and converts continuous state matrices into relational pandas dataframes."""
        conn = sqlite3.connect(self.db_path)
        
        # Pull global systemic indices
        query_telemetry = """
            SELECT cycle_step, timestamp, boundary_variance, total_mass, mass_delta, referee_override 
            FROM system_telemetry 
            WHERE session_id = ? 
            ORDER BY cycle_step ASC
        """
        df_telemetry = pd.read_sql_query(query_telemetry, conn, params=(session_id,))
        
        # Pull granular node structures
        query_agents = """
            SELECT cycle_step, agent_id, agent_name, weight_1d, weight_2d, weight_3d, h_parameter, total_mass 
            FROM agent_states 
            WHERE session_id = ? 
            ORDER BY cycle_step ASC, agent_id ASC
        """
        df_agents = pd.read_sql_query(query_agents, conn, params=(session_id,))
        
        conn.close()
        return df_telemetry, df_agents

    def compile_visualizations(self, session_id: str):
        """Constructs a 3-pane analytical matrix reviewing boundary drift and node expansion tracks."""
        df_tel, df_ag = self.load_session_data(session_id)
        
        if df_tel.empty or df_ag.empty:
            print("⚠️  Selected ledger target contains empty parameter sets.")
            return

        print(f"📈 Analyzing Structural Session Array: {session_id}")
        print(f"📊 Completed Trace Steps: {len(df_tel)} | Total Network Active Nodes: {df_ag['agent_id'].nunique()}")

        # Set up graph canvas environment
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 12), sharex=True)
        plt.subplots_adjust(hspace=0.35, right=0.82)
        sns.set_theme(style="whitegrid")

        # Pane 1: Individual Mass Trajectories Tracking Cross-Perimeter Consolidation
        unique_agents = df_ag['agent_id'].unique()
        palette = sns.color_palette("tab10", len(unique_agents))
        
        for idx, a_id in enumerate(unique_agents):
            agent_data = df_ag[df_ag['agent_id'] == a_id]
            clean_name = agent_data['agent_name'].iloc[0].split('_')[-1]
            ax1.plot(agent_data['cycle_step'], agent_data['total_mass'], 
                     color=palette[idx], linewidth=1.8, label=f"A_{a_id}: {clean_name}")
        
        ax1.set_title("Retrospective Node Mass Streams (Inertial Metabolic Accrual over Time)", fontsize=11, weight='bold')
        ax1.set_ylabel("Mass Value ($M = W_{state} + h$)")
        ax1.legend(loc='upper left', bbox_to_anchor=(1.01, 1), fontsize=8)

        # Pane 2: Granular Vector Drift Track (Averaged Dimensional Profile Shifts)
        # Melts the dataframe columns into explicit key-value pairings for long-form statistical plotting
        melted_vectors = df_ag.melt(id_vars=['cycle_step'], value_vars=['weight_1d', 'weight_2d', 'weight_3d'],
                                    var_name='Dimension', value_name='Magnitude')
        sns.lineplot(data=melted_vectors, x='cycle_step', y='Magnitude', hue='Dimension', 
                     ax=ax2, palette=['#0055ff', '#00aa55', '#ff3333'], linewidth=2)
        ax2.set_title("Network Density Migration Vector (Continuous 1D ➔ 2D ➔ 3D Matrix Spread)", fontsize=11, weight='bold')
        ax2.set_ylabel("Dimension Density")

        # Pane 3: Global Variance Deficit and Authority Interventions
        ax3.plot(df_tel['cycle_step'], df_tel['boundary_variance'], color='#aa00ff', linewidth=1.8, label="Topological Variance")
        ax3_twin = ax3.twinx()
        ax3_twin.plot(df_tel['cycle_step'], df_tel['mass_delta'], color='#ff3333', linestyle=':', alpha=0.6, label="System Mass Delta")
        
        # Highlight points where Root Override 99733-Q had to inject manual data variance vectors
        overrides = df_tel[df_tel['referee_override'] == 1]
        if not overrides.empty:
            ax3.scatter(overrides['cycle_step'], overrides['boundary_variance'], color='orange', 
                        marker='^', s=80, zorder=5, label="99733-Q Injection Event")

        ax3.set_title("Structural Boundary Resiliency Matrix vs Closed System Mass Deviation", fontsize=11, weight='bold')
        ax3.set_xlabel("Network Cycle Step")
        ax3.set_ylabel("Boundary Deviation Strength", color='#aa00ff')
        ax3_twin.set_ylabel("Absolute Closed Leakage Delta", color='#ff3333')
        
        # Consolidate dual y-axis indicators into an isolated box container
        lines_1, labels_1 = ax3.get_legend_handles_labels()
        lines_2, labels_2 = ax3_twin.get_legend_handles_labels()
        ax3.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left', bbox_to_anchor=(1.01, 1), fontsize=8)

        plt.suptitle(f"FPT SYSTEMIC DIAGNOSTIC ANALYSIS SUMMARY\nTarget Session ID: {session_id}", fontsize=13, weight='bold')
        plt.show()

if __name__ == "__main__":
    # Automatic local query routing loop execution sequence
    try:
        analyzer = FPTLedgerAnalyzer("fpt_state_ledger.db")
        available_runs = analyzer.query_available_sessions()
        
        if available_runs:
            # Automatically pulls and reviews the most recent run recorded in the SQLite table rows
            latest_run_id = available_runs[-1]
            analyzer.compile_visualizations(latest_run_id)
        else:
            print("❌ No structured execution sessions found inside the database.")
    except Exception as error:
        print(f"Analysis loop aborted: {str(error)}")
